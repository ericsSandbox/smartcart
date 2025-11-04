import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from ..providers import flipp, basket
from ..providers import savemart, walmart
from ..providers import weekly_ads
from ..providers.utils import normalize_ingredient_query
from ..providers import raleys_pdf

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/settings/{household_id}", response_model=schemas.HouseholdSettings)
def get_settings(household_id: int, db: Session = Depends(get_db)):
    settings = crud.get_household_settings(db, household_id)
    if not settings:
        # Return a default settings object (not persisted yet)
        return schemas.HouseholdSettings(
            id=0,
            household_id=household_id,
            pricing_enabled=False,
            zip_code=None,
            latitude=None,
            longitude=None,
            radius_miles=5.0,
        )
    return settings


@router.post("/settings", response_model=schemas.HouseholdSettings)
def upsert_settings(payload: schemas.HouseholdSettingsCreate, db: Session = Depends(get_db)):
    # Validate household exists
    if not crud.get_household(db, payload.household_id):
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.upsert_household_settings(db, payload)


@router.post("/offers", response_model=schemas.PricingOffersResponse)
def get_offers(payload: schemas.PricingOffersRequest, db: Session = Depends(get_db)):
    settings = crud.get_household_settings(db, payload.household_id)
    if not settings or not settings.pricing_enabled:
        raise HTTPException(status_code=400, detail="Pricing service not enabled for this household")

    # Normalize the query to extract core ingredient
    normalized_query = normalize_ingredient_query(payload.query)
    print(f"[Pricing] Original query: '{payload.query}', Normalized: '{normalized_query}'")

    # Decide location priority: lat/lng over zip
    lat = settings.latitude
    lng = settings.longitude
    zip_code = settings.zip_code
    radius = payload.radius_miles or settings.radius_miles or 5.0

    offers = []

    # Try weekly ad scrapers FIRST (most reliable, stores want you to see these)
    try:
        print(f"[Pricing] Calling weekly_ads.fetch_all_weekly_ads with query='{normalized_query}'")
        weekly_offers = weekly_ads.fetch_all_weekly_ads(normalized_query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius)
        offers += weekly_offers
        if weekly_offers:
            print(f"Got {len(weekly_offers)} offers from weekly ads")
    except Exception as e:
        print(f"Weekly ads failed: {e}")

    # Try live inventory scrapers (likely blocked but worth a shot)
    try:
        offers += walmart.fetch_offers(normalized_query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius)
    except Exception as e:
        print(f"Walmart scraper failed: {e}")
    
    try:
        offers += savemart.fetch_offers(normalized_query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius)
    except Exception as e:
        print(f"Save Mart scraper failed: {e}")

    # Try API providers if keys are present
    try:
        offers += flipp.fetch_offers(normalized_query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius)
    except Exception:
        pass
    try:
        offers += basket.fetch_offers(normalized_query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius)
    except Exception:
        pass

    # If nothing found, return empty (no demo fallback)
    if len(offers) == 0:
        print(f"No offers found for '{normalized_query}'")

    # Normalize: ensure unique (store, price, url) and sort by price if available
    seen = set()
    normalized = []
    for o in offers:
        provider = o.get('provider') or 'unknown'
        store = o.get('store') or 'Unknown Store'
        price = o.get('price')
        key = (provider, store, price, o.get('url'))
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            'provider': provider,
            'store': store,
            'price': price,
            'unit': o.get('unit'),
            'url': o.get('url'),
            'promo_text': o.get('promo_text'),
            'distance_miles': o.get('distance_miles'),
        })

    def sort_key(x):
        return (x['price'] is None, x['price'])

    normalized.sort(key=sort_key)

    return schemas.PricingOffersResponse(offers=normalized, normalized_query=normalized_query)


@router.get("/circulars", response_model=list[dict])
def get_current_circulars():
    """
    Get current ad circulars from all stores.
    Returns circular metadata with available products and prices.
    """
    all_circulars = []
    
    # Fetch Raley's PDFs with products (if available)
    try:
        raleys_circulars = raleys_pdf.fetch_raleys_pdf_circulars()
        all_circulars.extend(raleys_circulars)
    except Exception as e:
        print(f"[Circulars] Failed to fetch Raley's circulars: {e}")
    
    # TODO: Add Safeway, Smith's, Sprouts, etc.
    
    return all_circulars

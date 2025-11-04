"""
API endpoints for circular items and ad circulars tab.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CircularItem, CircularItemResponse
from app import crud_circular
from app.services.circular_loader import get_loader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/circulars", tags=["circulars"])


@router.get("/items", response_model=List[CircularItemResponse])
def get_circular_items(
    retailer: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get items from circulars with optional filtering."""
    items = crud_circular.get_circular_items(
        db,
        retailer=retailer,
        category=category,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/search")
def search_circular_items(
    q: str,
    retailer: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Search for items in circulars."""
    if not q or len(q) < 2:
        return {"results": [], "query": q}
    
    items = crud_circular.search_circular_items(db, q, retailer=retailer)
    
    return {
        "query": q,
        "count": len(items),
        "results": [
            {
                "retailer": item.retailer,
                "item_name": item.item_name,
                "price": item.price,
                "unit": item.unit,
                "category": item.category,
            }
            for item in items
        ]
    }


@router.get("/retailers")
def get_retailers(db: Session = Depends(get_db)):
    """Get list of all available retailers."""
    retailers = crud_circular.get_retailers(db)
    return {"retailers": retailers}


@router.get("/retailers/{retailer}/categories")
def get_retailer_categories(
    retailer: str,
    db: Session = Depends(get_db),
):
    """Get categories for a specific retailer."""
    categories = crud_circular.get_categories_for_retailer(db, retailer)
    return {
        "retailer": retailer,
        "categories": categories,
    }


@router.get("/summary")
def get_circular_summary(db: Session = Depends(get_db)):
    """Get summary of loaded circulars."""
    summary = crud_circular.get_circular_summary(db)
    return summary


@router.post("/reload/{retailer}")
def reload_retailer(
    retailer: str,
    db: Session = Depends(get_db),
):
    """Manually reload circulars for a specific retailer."""
    loader = get_loader()
    result = loader.reload_retailer(db, retailer)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/find-price")
def find_price(
    item_name: str,
    retailer: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Find price for a shopping list item in loaded circulars."""
    if not item_name:
        return {"error": "item_name required"}
    
    price = crud_circular.find_price_for_item(db, item_name, retailer=retailer)
    
    return {
        "item_name": item_name,
        "retailer": retailer,
        "price": price,
        "found": price is not None,
    }

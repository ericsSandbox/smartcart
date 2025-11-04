"""
Weekly Ad scraper for major grocery chains.
Scrapes digital circulars and sale pages instead of live inventory.
"""
from typing import List, Dict, Optional
from .scraper_base import GroceryScraper
import urllib.parse
import re
import os


def _tokenize(s: str) -> List[str]:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    parts = [p for p in s.split() if p]
    # naive singularization for common plurals
    singular = []
    for p in parts:
        if len(p) > 3 and p.endswith('es'):
            singular.append(p[:-2])
        elif len(p) > 3 and p.endswith('s'):
            singular.append(p[:-1])
        else:
            singular.append(p)
    return singular


def _query_variants(query: str) -> List[List[str]]:
    """Generate token sets representing acceptable matches.
    Keeps it simple and dependency-free.
    """
    base = _tokenize(query)
    variants: List[List[str]] = [base]
    q = " ".join(base)
    # synonyms
    syn_map = {
        'ground beef': ['ground beef', 'hamburger', 'hamburger meat', 'minced beef'],
        'onion': ['onion', 'yellow onion', 'white onion', 'red onion'],
        'jalapeno': ['jalapeno', 'jalapeno pepper', 'jalapeno peppers'],
    }
    for k, alts in syn_map.items():
        if k in q:
            for a in alts:
                variants.append(_tokenize(a))
    # If query is two words, also allow either token alone (e.g., "ground"+"beef" -> "beef")
    if len(base) == 2:
        variants.append([base[0]])
        variants.append([base[1]])
    return variants


def _matches_query(query: str, text: str) -> bool:
    text_tokens = set(_tokenize(text))
    for var in _query_variants(query):
        # require at least all tokens in variant to be present or strong partial overlap
        var_set = set(var)
        if var_set and var_set.issubset(text_tokens):
            return True
        # Allow partial for produce/meat (at least 1 significant token)
        if len(var_set) >= 2 and len(var_set.intersection(text_tokens)) >= 1:
            return True
    return False


class WalmartWeeklyAdScraper(GroceryScraper):
    """Scrape Walmart's weekly ad/rollback deals."""
    
    def __init__(self):
        super().__init__('Walmart Weekly Ad', 'https://www.walmart.com')
    
    def search(self, query: str, zip_code: Optional[str] = None,
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """
        Search Walmart's weekly ad and rollback deals.
        Uses their savings catcher / weekly ad page.
        """
        offers = []
        
        try:
            # Walmart's weekly ad page
            ad_url = f"{self.base_url}/shop/deals/rollback"
            
            soup = self.fetch_html(ad_url)
            if not soup:
                return offers
            
            # Look for product cards in the deals section
            # Walmart uses various card patterns
            for card in soup.find_all(['div', 'article'], limit=100):
                card_text = card.get_text(' ', strip=True)
                
                # Skip if our query doesn't reasonably match this card
                if not _matches_query(query, card_text):
                    continue
                
                try:
                    # Find product name
                    name_elem = card.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'prod.*name|title', re.I))
                    if not name_elem:
                        name_elem = card.find('a', href=re.compile(r'/ip/'))
                    
                    product_name = name_elem.get_text(strip=True) if name_elem else None
                    if not product_name:
                        continue
                    
                    # Find price
                    price_elem = card.find(['span', 'div'], class_=re.compile(r'price', re.I))
                    price = None
                    if price_elem:
                        price = self.extract_price(price_elem.get_text())
                    
                    # Find link
                    link = card.find('a', href=True)
                    product_url = None
                    if link:
                        href = link['href']
                        product_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    if product_name and price:
                        offers.append({
                            'provider': 'Walmart Weekly Ad',
                            'store': 'Walmart',
                            'price': price,
                            'unit': None,
                            'url': product_url,
                            'promo_text': 'Rollback',
                            'distance_miles': None,
                            'product_name': product_name,
                        })
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"[Walmart Weekly Ad] Failed: {e}")
        
        return offers


class SafewayWeeklyAdScraper(GroceryScraper):
    """Scrape Safeway's weekly ad."""
    
    def __init__(self):
        super().__init__('Safeway Weekly Ad', 'https://www.safeway.com')
    
    def search(self, query: str, zip_code: Optional[str] = None,
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """Search Safeway's weekly ad for deals."""
        offers = []
        
        try:
            # Safeway's weekly ad is often at /weeklyad or /deals
            ad_url = f"{self.base_url}/deals.html"
            
            soup = self.fetch_html(ad_url)
            if not soup:
                return offers
            
            # Search for matching products
            for card in soup.find_all(['div', 'article'], limit=100):
                card_text = card.get_text(' ', strip=True)
                if not _matches_query(query, card_text):
                    continue
                
                try:
                    # Extract product info
                    name_elem = card.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'prod.*name|title|item', re.I))
                    product_name = name_elem.get_text(strip=True) if name_elem else None
                    
                    price_elem = card.find(['span', 'div'], class_=re.compile(r'price|cost', re.I))
                    price = self.extract_price(price_elem.get_text()) if price_elem else None
                    
                    if product_name and price:
                        offers.append({
                            'provider': 'Safeway Weekly Ad',
                            'store': 'Safeway',
                            'price': price,
                            'unit': None,
                            'url': None,
                            'promo_text': 'Weekly Ad',
                            'distance_miles': None,
                            'product_name': product_name,
                        })
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"[Safeway Weekly Ad] Failed: {e}")
        
        return offers


def fetch_walmart_weekly(query: str, *, zip_code: Optional[str] = None,
                         lat: Optional[float] = None, lng: Optional[float] = None,
                         radius_miles: float = 5.0) -> List[Dict]:
    """Get Walmart weekly ad deals."""
    scraper = WalmartWeeklyAdScraper()
    return scraper.search(query, zip_code, lat, lng, radius_miles)


def fetch_safeway_weekly(query: str, *, zip_code: Optional[str] = None,
                         lat: Optional[float] = None, lng: Optional[float] = None,
                         radius_miles: float = 5.0) -> List[Dict]:
    """Get Safeway weekly ad deals."""
    scraper = SafewayWeeklyAdScraper()
    return scraper.search(query, zip_code, lat, lng, radius_miles)


def fetch_all_weekly_ads(query: str, *, zip_code: Optional[str] = None,
                         lat: Optional[float] = None, lng: Optional[float] = None,
                         radius_miles: float = 5.0) -> List[Dict]:
    """
    Aggregate pricing from all supported stores.
    Uses curated product database for accurate circular prices.
    """
    from . import smiths, raleys_db_fetcher
    
    all_offers = []
    
    # Try each store's pricing source, ordered by preference
    scrapers = [
        ('Safeway', fetch_safeway_weekly),
        ('Smith\'s', smiths.fetch_smiths_weekly),
        ('Raley\'s', raleys_db_fetcher.fetch_raleys_from_database),  # Curated product database
    ]
    
    # Walmart weekly deals are often general merchandise; include only if enabled
    if os.getenv('WEEKLY_WALMART_ENABLED', '').lower() in {'1', 'true', 'yes', 'on'}:
        scrapers.append(('Walmart', fetch_walmart_weekly))
    
    # TODO: Add Sprouts, Whole Foods, Trader Joe's
    
    for store_name, fetch_func in scrapers:
        try:
            print(f"[Weekly Ads] Calling {store_name}...")
            offers = fetch_func(query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius_miles)
            all_offers.extend(offers)
            if offers:
                print(f"[Weekly Ads] Found {len(offers)} offers from {store_name}")
            else:
                print(f"[Weekly Ads] No offers from {store_name}")
        except Exception as e:
            print(f"[Weekly Ads] {store_name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    return all_offers

"""
Walmart grocery scraper.
Scrapes walmart.com for product prices.
"""
from typing import List, Dict, Optional
from .scraper_base import GroceryScraper
import urllib.parse
import json
import re


class WalmartScraper(GroceryScraper):
    """Scraper for Walmart stores."""
    
    def __init__(self):
        super().__init__('Walmart', 'https://www.walmart.com')
    
    def search(self, query: str, zip_code: Optional[str] = None,
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """
        Search Walmart for products matching query.
        
        Walmart's site has an API endpoint that returns JSON data.
        """
        offers = []
        
        try:
            # Walmart search API endpoint
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'sort': 'best_match',
                'page': 1,
                'affinityOverride': 'default'
            }
            
            # Walmart returns JSON embedded in the HTML in a __NEXT_DATA__ script tag
            # or we can try their API directly
            soup = self.fetch_html(f"{search_url}?{urllib.parse.urlencode(params)}")
            if not soup:
                return offers
            
            # Find the __NEXT_DATA__ script with product data
            next_data_script = soup.find('script', id='__NEXT_DATA__', type='application/json')
            
            if next_data_script and next_data_script.string:
                try:
                    data = json.loads(next_data_script.string)
                    
                    # Navigate the data structure to find products
                    # Structure varies but typically: props > pageProps > initialData > searchResult > itemStacks
                    page_props = data.get('props', {}).get('pageProps', {})
                    initial_data = page_props.get('initialData', {})
                    search_result = initial_data.get('searchResult', {})
                    
                    # Products are usually in itemStacks
                    item_stacks = search_result.get('itemStacks', [])
                    
                    for stack in item_stacks[:20]:  # Limit to first 20
                        items = stack.get('items', [])
                        for item in items:
                            try:
                                product_name = item.get('name') or item.get('title', '')
                                if not product_name:
                                    continue
                                
                                # Price info
                                price_info = item.get('priceInfo', {})
                                current_price = price_info.get('currentPrice', {})
                                price = current_price.get('price')
                                if price is None:
                                    price = current_price.get('priceString', '')
                                    price = self.extract_price(str(price))
                                
                                # Unit price
                                unit_price = price_info.get('unitPrice', '')
                                
                                # Product URL
                                product_url = None
                                if item.get('canonicalUrl'):
                                    product_url = f"{self.base_url}{item['canonicalUrl']}"
                                elif item.get('usItemId'):
                                    product_url = f"{self.base_url}/ip/{item['usItemId']}"
                                
                                # Badges (sale, rollback, etc.)
                                badges = item.get('badges', {})
                                flags = badges.get('flags', [])
                                promo_text = None
                                if flags:
                                    promo_text = ', '.join([f.get('text', '') for f in flags if f.get('text')])
                                
                                if product_name and price:
                                    offers.append({
                                        'provider': 'Walmart (scraped)',
                                        'store': 'Walmart',
                                        'price': float(price) if price else None,
                                        'unit': unit_price if unit_price else None,
                                        'url': product_url,
                                        'promo_text': promo_text,
                                        'distance_miles': None,
                                        'product_name': product_name,
                                    })
                            
                            except Exception as e:
                                print(f"[Walmart] Error parsing item: {e}")
                                continue
                
                except json.JSONDecodeError as e:
                    print(f"[Walmart] Failed to parse __NEXT_DATA__: {e}")
        
        except Exception as e:
            print(f"[Walmart] Search failed: {e}")
        
        return offers


def fetch_offers(query: str, *, zip_code: Optional[str] = None,
                 lat: Optional[float] = None, lng: Optional[float] = None,
                 radius_miles: float = 5.0) -> List[Dict]:
    """Scrape Walmart for offers matching query."""
    scraper = WalmartScraper()
    return scraper.search(query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius_miles)

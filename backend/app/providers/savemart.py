"""
Save Mart grocery store scraper.
Scrapes shop.savemart.com for product prices.
"""
from typing import List, Dict, Optional
from .scraper_base import GroceryScraper
import urllib.parse


class SaveMartScraper(GroceryScraper):
    """Scraper for Save Mart stores."""
    
    def __init__(self):
        super().__init__('Save Mart', 'https://shop.savemart.com')
    
    def search(self, query: str, zip_code: Optional[str] = None,
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """
        Search Save Mart for products matching query.
        
        Save Mart uses a modern web app (likely React/Next.js) with API endpoints.
        The search results are loaded dynamically via JavaScript.
        
        Strategy:
        1. Find the search API endpoint by inspecting network traffic
        2. Set store location if zip provided
        3. Query the search API
        4. Parse JSON response for product data
        """
        offers = []
        
        try:
            # Save Mart uses an internal API for search
            # Typical pattern: /api/product/search?q=sugar&store=...
            # We need to inspect their actual endpoint structure
            
            # For now, try the storefront search URL and parse HTML
            search_url = f"{self.base_url}/store/savemart/search"
            params = {'q': query}
            
            # If zip provided, we'd need to set store preference first
            # This typically requires cookies or API calls to set location
            if zip_code:
                # TODO: Implement location setting via their API
                pass
            
            soup = self.fetch_html(f"{search_url}?{urllib.parse.urlencode(params)}")
            if not soup:
                return offers
            
            # Parse product cards
            # Modern grocery sites typically have product cards with:
            # - Product name in h3/h4 or data-testid="product-title"
            # - Price in span with class like "price" or data-testid="product-price"
            # - Link to product detail page
            
            # Look for common product card patterns
            product_cards = soup.find_all(['article', 'div'], class_=lambda c: c and any(
                x in str(c).lower() for x in ['product-card', 'product-item', 'product_card', 'grid-item']
            ))
            
            if not product_cards:
                # Try data attributes
                product_cards = soup.find_all(attrs={'data-testid': lambda x: x and 'product' in x.lower()})
            
            for card in product_cards[:20]:  # Limit to first 20 results
                try:
                    # Extract product name
                    name_elem = card.find(['h2', 'h3', 'h4', 'span'], class_=lambda c: c and any(
                        x in str(c).lower() for x in ['title', 'name', 'product-name']
                    ))
                    if not name_elem:
                        name_elem = card.find(attrs={'data-testid': lambda x: x and 'title' in str(x).lower()})
                    
                    product_name = name_elem.get_text(strip=True) if name_elem else None
                    if not product_name:
                        continue
                    
                    # Extract price
                    price_elem = card.find(['span', 'div'], class_=lambda c: c and 'price' in str(c).lower())
                    if not price_elem:
                        price_elem = card.find(attrs={'data-testid': lambda x: x and 'price' in str(x).lower()})
                    
                    price_text = price_elem.get_text(strip=True) if price_elem else None
                    price = self.extract_price(price_text) if price_text else None
                    
                    # Extract link
                    link_elem = card.find('a', href=True)
                    product_url = None
                    if link_elem and link_elem.get('href'):
                        href = link_elem['href']
                        product_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    
                    # Extract unit if available
                    unit_elem = card.find(['span', 'div'], class_=lambda c: c and any(
                        x in str(c).lower() for x in ['unit', 'size', 'quantity']
                    ))
                    unit = unit_elem.get_text(strip=True) if unit_elem else None
                    
                    # Extract promo text
                    promo_elem = card.find(['span', 'div'], class_=lambda c: c and any(
                        x in str(c).lower() for x in ['promo', 'sale', 'deal', 'badge']
                    ))
                    promo_text = promo_elem.get_text(strip=True) if promo_elem else None
                    
                    if product_name and price:
                        offers.append({
                            'provider': 'Save Mart (scraped)',
                            'store': 'Save Mart',
                            'price': price,
                            'unit': unit,
                            'url': product_url,
                            'promo_text': promo_text,
                            'distance_miles': None,  # Would need geocoding
                            'product_name': product_name,
                        })
                
                except Exception as e:
                    print(f"[Save Mart] Error parsing product card: {e}")
                    continue
        
        except Exception as e:
            print(f"[Save Mart] Search failed: {e}")
        
        return offers


def fetch_offers(query: str, *, zip_code: Optional[str] = None,
                 lat: Optional[float] = None, lng: Optional[float] = None,
                 radius_miles: float = 5.0) -> List[Dict]:
    """Scrape Save Mart for offers matching query."""
    scraper = SaveMartScraper()
    return scraper.search(query, zip_code=zip_code, lat=lat, lng=lng, radius_miles=radius_miles)

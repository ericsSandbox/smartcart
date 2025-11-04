"""
Raley's scraper using simple HTTP requests + BeautifulSoup.
Much simpler and more reliable than Selenium.
"""

import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache for search results to avoid hammering their servers
_search_cache = {}

def search_raleys(query: str, zip_code: str = "89503", timeout: int = 10) -> List[Dict]:
    """
    Search Raley's website for products using simple HTTP requests.
    
    Args:
        query: Product search term
        zip_code: Store location (for context, though not used in direct search)
        timeout: Request timeout
    
    Returns:
        List of products with prices
    """
    products = []
    
    # Check cache first
    cache_key = f"{query}:{zip_code}"
    if cache_key in _search_cache:
        logger.debug(f"Using cached results for '{query}'")
        return _search_cache[cache_key]
    
    try:
        logger.info(f"Searching Raley's for '{query}'...")
        
        # Build search URL
        search_url = f"https://www.raleys.com/search?q={requests.utils.quote(query)}"
        
        # Make request with browser-like headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(search_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        logger.debug(f"Got response: {response.status_code}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract JSON data from page if it's using Next.js
        # Look for __NEXT_DATA__ script tag
        try:
            next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
            if next_data_script:
                logger.debug("Found Next.js data")
                data = json.loads(next_data_script.string)
                # Try to find products in the data structure
                products_data = extract_from_json(data, query)
                if products_data:
                    logger.info(f"Extracted {len(products_data)} products from JSON")
                    _search_cache[cache_key] = products_data
                    return products_data
        except Exception as e:
            logger.debug(f"Could not parse Next.js JSON: {e}")
        
        # Fallback: try to parse from HTML structure
        logger.debug("Falling back to HTML parsing...")
        
        # Look for product containers
        product_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile('product', re.I))
        
        logger.debug(f"Found {len(product_containers)} product containers")
        
        for container in product_containers[:50]:  # Limit to first 50
            try:
                # Extract product name
                name_elem = container.find(['h3', 'h4', 'a'], class_=re.compile('(name|title|product)', re.I))
                if not name_elem:
                    name_elem = container.find(['h3', 'h4', 'a'])
                
                if not name_elem:
                    continue
                
                product_name = name_elem.get_text(strip=True)
                if not product_name or len(product_name) < 2:
                    continue
                
                # Extract price
                price = None
                price_elem = container.find(['span', 'div'], class_=re.compile('(price|cost)', re.I))
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract numeric price
                    price_match = re.search(r'\$?([\d.]+)', price_text)
                    if price_match:
                        try:
                            price = float(price_match.group(1))
                        except ValueError:
                            pass
                
                # Extract unit
                unit = "each"
                unit_elem = container.find(['span', 'div'], class_=re.compile('unit', re.I))
                if unit_elem:
                    unit_text = unit_elem.get_text(strip=True)
                    if 'lb' in unit_text.lower():
                        unit = 'lb'
                    elif 'oz' in unit_text.lower():
                        unit = 'oz'
                    elif 'ea' in unit_text.lower():
                        unit = 'each'
                
                products.append({
                    'provider': "Raley's",
                    'store': "Raley's",
                    'product_name': product_name,
                    'price': price,
                    'unit': unit,
                    'url': 'https://www.raleys.com',
                    'promo_text': '',
                    'distance_miles': 2.5,
                })
                
                logger.debug(f"  Found: {product_name} - ${price}/{unit if price else 'N/A'}")
                
            except Exception as e:
                logger.debug(f"Error parsing product container: {e}")
                continue
        
        logger.info(f"Found {len(products)} products for '{query}'")
        
        # Cache the results
        _search_cache[cache_key] = products
        return products
        
    except Exception as e:
        logger.error(f"Error searching Raley's: {e}")
        return []


def extract_from_json(data: dict, query: str) -> List[Dict]:
    """
    Try to extract product data from Next.js JSON data structure.
    """
    products = []
    
    try:
        # Next.js stores page props under different keys
        # Common structures: pageProps.initialState, pageProps.data, etc.
        props = data.get('props', {}).get('pageProps', {})
        
        # Look for products in various locations
        if 'products' in props:
            products_data = props['products']
            if isinstance(products_data, list):
                for item in products_data[:50]:
                    try:
                        products.append({
                            'provider': "Raley's",
                            'store': "Raley's",
                            'product_name': item.get('name', item.get('title', '')),
                            'price': float(item.get('price', 0)) if item.get('price') else None,
                            'unit': item.get('unit', 'each'),
                            'url': 'https://www.raleys.com',
                            'promo_text': item.get('promotion', ''),
                            'distance_miles': 2.5,
                        })
                    except Exception as e:
                        logger.debug(f"Error extracting product from JSON: {e}")
                        continue
        
        return products
    except Exception as e:
        logger.debug(f"Error extracting JSON data: {e}")
        return []


def fetch_raleys_http(query: str, *, zip_code: Optional[str] = None,
                     lat: Optional[float] = None, lng: Optional[float] = None,
                     radius_miles: float = 5.0) -> List[Dict]:
    """
    Fetch Raley's product prices using simple HTTP requests.
    Entry point for the weekly_ads pipeline.
    
    Args:
        query: Product search term
        zip_code: Store location (default: Reno 89503)
        **kwargs: Additional arguments (ignored)
    
    Returns:
        List of products with prices
    """
    if not query:
        return []
    
    if not zip_code:
        zip_code = "89503"  # Default to Reno
    
    try:
        return search_raleys(query, zip_code)
    except Exception as e:
        logger.error(f"HTTP search failed: {e}")
        return []

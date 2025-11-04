"""
Raley's scraper using Playwright for JavaScript rendering.
Playwright is faster and more reliable than Selenium in containerized environments.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# Cache to avoid repeated searches in same session
_search_cache: Dict[str, List[Dict]] = {}


async def search_raleys_async(query: str, zip_code: str = "89503") -> List[Dict[str, Any]]:
    """
    Search Raley's for products using Playwright with async/await.
    
    Args:
        query: Product search term (e.g., "onion")
        zip_code: Store location zip code
        
    Returns:
        List of products with name, price, section info
    """
    
    cache_key = f"{query}:{zip_code}"
    if cache_key in _search_cache:
        logger.info(f"[Raley's Playwright] Using cached results for '{query}'")
        return _search_cache[cache_key]
    
    products = []
    
    try:
        async with async_playwright() as p:
            # Launch browser
            logger.info("[Raley's Playwright] Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )
            
            # Create new context with realistic viewport
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Create new page
            page = await context.new_page()
            
            # Set longer timeout
            page.set_default_timeout(45000)  # 45 seconds
            page.set_default_navigation_timeout(45000)
            
            try:
                # Navigate to search page
                search_url = f"https://www.raleys.com/search?q={query}"
                logger.info(f"[Raley's Playwright] Navigating to {search_url}")
                
                # Use domcontentloaded instead of networkidle to avoid long waits
                await page.goto(search_url, wait_until="domcontentloaded")
                logger.info("[Raley's Playwright] Page structure loaded, waiting for JS to fetch products...")
                
                # The page loads structure but products come via JS/API
                # Wait for product links to appear (with extended timeout)
                logger.info("[Raley's Playwright] Waiting for product links to appear...")
                try:
                    await page.wait_for_selector('a[href*="/product/"]', timeout=20000)
                    logger.info("[Raley's Playwright] Product links found!")
                except PlaywrightTimeoutError:
                    logger.warning("[Raley's Playwright] Product links timeout, proceeding anyway...")
                
                # Extra wait to ensure all JS-loaded content is available
                logger.info("[Raley's Playwright] Waiting for JS execution...")
                await page.wait_for_timeout(5000)  # 5 second buffer
                
                # Get final page content
                content = await page.content()
                logger.info(f"[Raley's Playwright] Final HTML size: {len(content)} bytes")
                
                # Try to extract products from rendered HTML
                from bs4 import BeautifulSoup
                import re
                
                soup = BeautifulSoup(content, "html.parser")
                
                # Find all product links
                product_links = soup.find_all('a', href=lambda x: x and "/product/" in x)
                logger.info(f"[Raley's Playwright] Found {len(product_links)} product links")
                
                # Extract unique products
                seen_products = set()
                for link in product_links[:50]:  # Limit to first 50 links
                    try:
                        href = link.get('href', '')
                        
                        # Extract product ID and name from href
                        match = re.search(r'/product/([^/]+)/([^/]+)', href)
                        if not match:
                            continue
                        
                        product_id = match.group(1)
                        if product_id in seen_products:
                            continue
                        
                        seen_products.add(product_id)
                        
                        product = {}
                        product["id"] = product_id
                        product["store"] = "Raley's"  # Set store name
                        
                        # Get product name from href (URL slug)
                        name_slug = match.group(2).replace('-', ' ').title()
                        product["name"] = name_slug
                        
                        # Try to find price - extract from parent and nearby text
                        parent = link.parent
                        found_price = False
                        
                        # Search in parent and nearby elements (up to 6 levels)
                        for search_level in range(6):
                            if parent is None or found_price:
                                break
                            
                            # Get parent text and look for price patterns
                            parent_text = parent.get_text(strip=True)
                            
                            # First try: look for prices with $ prefix (most reliable)
                            dollar_prices = re.findall(r'\$([\d]{1,3}\.[\d]{2})', parent_text)
                            if dollar_prices:
                                valid_prices = []
                                for pm in dollar_prices:
                                    try:
                                        price_val = float(pm)
                                        if 0.50 <= price_val <= 100:
                                            valid_prices.append(price_val)
                                    except ValueError:
                                        continue
                                
                                if valid_prices:
                                    product["price"] = valid_prices[0]  # Take first $ price found
                                    found_price = True
                                    break
                            
                            # Second try: look for prices with unit suffix (e.g., /lb, ea)
                            unit_prices = re.findall(r'([\d]{1,3}\.[\d]{2})(?:/|ea|lb|each)', parent_text)
                            if unit_prices:
                                valid_prices = []
                                for pm in unit_prices:
                                    try:
                                        price_val = float(pm)
                                        if 0.50 <= price_val <= 100:
                                            valid_prices.append(price_val)
                                    except ValueError:
                                        continue
                                
                                if valid_prices:
                                    product["price"] = min(valid_prices)  # Take smallest
                                    found_price = True
                                    break
                            
                            parent = parent.parent
                        
                        # Add query as category
                        product["section"] = query
                        
                        # Keep products with at least name (price is optional)
                        if "name" in product:
                            products.append(product)
                    except Exception as e:
                        logger.debug(f"[Raley's Playwright] Error parsing product: {e}")
                        continue
                
                logger.info(f"[Raley's Playwright] Extracted {len(products)} products")
                
            except PlaywrightTimeoutError as e:
                logger.error(f"[Raley's Playwright] Page load timeout: {e}")
            except Exception as e:
                logger.error(f"[Raley's Playwright] Error during extraction: {e}")
            finally:
                await context.close()
                await browser.close()
        
        # Cache results
        _search_cache[cache_key] = products
        
    except Exception as e:
        logger.error(f"[Raley's Playwright] Fatal error: {e}")
        return []
    
    return products


def search_raleys(query: str, zip_code: str = "89503") -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for async Playwright search.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create new loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(search_raleys_async(query, zip_code))
            loop.close()
        else:
            result = loop.run_until_complete(search_raleys_async(query, zip_code))
    except RuntimeError:
        # No event loop, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(search_raleys_async(query, zip_code))
        loop.close()
    
    return result


def fetch_raleys_playwright(query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Entry point for weekly_ads pipeline.
    Searches for featured products based on query.
    
    Args:
        query: Product search term (optional, has default list if not provided)
        **kwargs: Additional args passed by pipeline (zip_code, lat, lng, etc.) - ignored
        
    Returns:
        List of products with pricing
    """
    logger.info("[Raley's Playwright] Starting products search...")
    
    # Search for specific query or default common products
    if query:
        queries = [query]
    else:
        queries = ["onion", "tri-tip steak", "wine"]
    
    all_products = []
    
    for q in queries:
        try:
            products = search_raleys(q)
            if products:
                all_products.extend(products)
                logger.info(f"[Raley's Playwright] Found {len(products)} products for '{q}'")
        except Exception as e:
            logger.error(f"[Raley's Playwright] Error searching for '{q}': {e}")
    
    logger.info(f"[Raley's Playwright] Total products: {len(all_products)}")
    return all_products

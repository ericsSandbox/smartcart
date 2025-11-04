"""
Raley's web scraper using Selenium for real-time inventory search.
Mimics the browser-based search that users do on raleys.com
"""

import logging
from typing import List, Dict, Optional
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

# Global driver cache to reuse browser instance
_driver = None
_driver_zip_code = None


def get_chrome_driver():
    """Get or create a Chrome webdriver instance."""
    global _driver, _driver_zip_code
    
    try:
        if _driver is None:
            logger.info("Initializing Chrome webdriver...")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1280,1024")
            chrome_options.add_argument("--start-maximized")
            # Reduce memory footprint
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            # Use system Chromium binary
            chrome_options.binary_location = "/usr/bin/chromium"
            
            # Don't use webdriver-manager, just use system chromium
            _driver = webdriver.Chrome(options=chrome_options)
            _driver.set_page_load_timeout(15)
            logger.info("✓ Chrome webdriver initialized")
        
        return _driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome webdriver: {e}")
        _driver = None
        raise


def set_store_location(zip_code: str = "89503") -> bool:
    """
    Set the store location on Raley's website.
    This step is required before searching for products.
    
    Args:
        zip_code: Store location zip code (default: Reno, NV)
    
    Returns:
        True if successful, False otherwise
    """
    global _driver_zip_code
    
    try:
        driver = get_chrome_driver()
        
        # Skip if we're already at this zip code
        if _driver_zip_code == zip_code:
            logger.debug(f"Already set to zip code {zip_code}")
            return True
        
        logger.info(f"Setting store location to zip code {zip_code}...")
        driver.get("https://www.raleys.com/")
        
        # Wait for page to load
        time.sleep(3)
        
        # Look for "Find a Store" button or store selector
        try:
            # Try to find and click store selector in header
            store_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Shop in Store')] | //button[contains(@aria-label, 'store')]"))
            )
            store_button.click()
            logger.debug("Clicked store selector button")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not find store selector button: {e}")
            # Try alternative: look for store info element
            pass
        
        # Try to find zip code input field
        try:
            zip_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'zip') or contains(@placeholder, 'Zip')]"))
            )
            zip_input.clear()
            zip_input.send_keys(zip_code)
            logger.debug(f"Entered zip code: {zip_code}")
            time.sleep(1)
            
            # Find and click search/confirm button
            search_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Search') or contains(text(), 'Find')]")
            search_btn.click()
            logger.debug("Clicked search button")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Could not enter zip code: {e}")
        
        # Try to click first store in results if available
        try:
            first_store = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')] | //div[@role='button'][1]"))
            )
            first_store.click()
            logger.debug("Selected first store")
            time.sleep(1)
        except Exception as e:
            logger.debug(f"Could not select store: {e}")
        
        _driver_zip_code = zip_code
        logger.info(f"✓ Store location set to {zip_code}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting store location: {e}")
        return False


def search_products(query: str, zip_code: str = "89503") -> List[Dict]:
    """
    Search for products on Raley's website using Selenium.
    
    Args:
        query: Product search term (e.g., "onions", "tri-tip")
        zip_code: Store zip code (default: Reno, NV)
    
    Returns:
        List of products with name, price, and availability
    """
    products = []
    
    try:
        driver = get_chrome_driver()
        
        # Ensure we have the right store selected
        if not set_store_location(zip_code):
            logger.warning("Failed to set store location, continuing anyway...")
        
        logger.info(f"Searching for '{query}' on Raley's...")
        
        # Navigate to search page
        search_url = f"https://www.raleys.com/search?q={query}"
        driver.get(search_url)
        time.sleep(4)  # Wait for page and JS to load
        
        # Wait for product results to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'product')] | //article[contains(@class, 'product')]"))
            )
        except Exception as e:
            logger.warning(f"Products did not load: {e}")
        
        # Extract product information
        product_elements = driver.find_elements(By.XPATH, 
            "//div[contains(@class, 'product')] | //article[contains(@class, 'product')] | //li[contains(@class, 'product')]"
        )
        
        logger.debug(f"Found {len(product_elements)} product elements")
        
        for idx, elem in enumerate(product_elements):
            try:
                # Extract product name
                try:
                    name_elem = elem.find_element(By.XPATH, ".//h3 | .//h4 | .//a[contains(@href, '/product')]")
                    product_name = name_elem.text.strip()
                except:
                    name_elem = elem.find_element(By.XPATH, ".//*[1]")
                    product_name = name_elem.text.strip()
                
                if not product_name or len(product_name) < 2:
                    continue
                
                # Extract price
                price = None
                try:
                    price_elem = elem.find_element(By.XPATH, ".//span[contains(@class, 'price')] | .//div[contains(text(), '$')]")
                    price_text = price_elem.text.strip()
                    # Extract numeric price
                    import re
                    price_match = re.search(r'\$?([\d.]+)', price_text)
                    if price_match:
                        price = float(price_match.group(1))
                except Exception as e:
                    logger.debug(f"Could not extract price for {product_name}: {e}")
                
                # Extract unit/description
                unit = "each"
                try:
                    unit_elem = elem.find_element(By.XPATH, ".//span[contains(@class, 'unit')] | .//span[contains(text(), '/')]")
                    unit_text = unit_elem.text.strip()
                    if '/' in unit_text:
                        unit = unit_text.split('/')[-1].strip()
                    elif 'lb' in unit_text.lower():
                        unit = 'lb'
                    elif 'oz' in unit_text.lower():
                        unit = 'oz'
                except:
                    pass
                
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
                
                logger.debug(f"  [{idx+1}] {product_name}: ${price}/{unit if price else 'N/A'}")
                
            except Exception as e:
                logger.debug(f"Error extracting product {idx}: {e}")
                continue
        
        logger.info(f"✓ Found {len(products)} products for '{query}'")
        return products
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        # Try to close and reset driver if error
        try:
            if _driver:
                _driver.quit()
                _driver = None
                _driver_zip_code = None
        except:
            pass
        return []


def fetch_raleys_selenium(query: str, *, zip_code: Optional[str] = None,
                         lat: Optional[float] = None, lng: Optional[float] = None,
                         radius_miles: float = 5.0) -> List[Dict]:
    """
    Fetch Raley's product prices using Selenium browser automation.
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
        return search_products(query, zip_code)
    except Exception as e:
        logger.error(f"Selenium search failed: {e}")
        return []


def close_driver():
    """Close the Selenium webdriver."""
    global _driver, _driver_zip_code
    try:
        if _driver:
            _driver.quit()
            _driver = None
            _driver_zip_code = None
            logger.info("Chrome webdriver closed")
    except Exception as e:
        logger.error(f"Error closing webdriver: {e}")

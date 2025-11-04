"""
Raley's weekly ad circular scraper.
Fetches and extracts product data from Raley's PDF circulars.
"""

import logging
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.providers.pdf_extractor import extract_products_from_pdf, find_product_in_circular


logger = logging.getLogger(__name__)


def get_session_with_retry():
    """Get requests session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        allowed_methods=["HEAD", "GET"],
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def verify_raleys_pdf_url(url: str) -> bool:
    """
    Verify that a Raley's PDF URL exists and is accessible.
    
    Args:
        url: PDF URL to verify
    
    Returns:
        True if URL is accessible, False otherwise
    """
    try:
        session = get_session_with_retry()
        response = session.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error verifying Raley's PDF URL: {e}")
        return False


def extract_offers_from_raleys_pdf(pdf_url: str, query: str = None) -> List[Dict[str, any]]:
    """
    Extract products and prices from Raley's PDF circular.
    Optionally filter by product query.
    
    Args:
        pdf_url: URL to Raley's PDF
        query: Optional product name to filter by
    
    Returns:
        List of products found in PDF with prices and promo text
    """
    try:
        logger.info(f"extract_offers_from_raleys_pdf called with query='{query}'")
        if query:
            logger.info(f"Searching for '{query}' in Raley's PDF using OCR...")
            products = find_product_in_circular(pdf_url, query)
            logger.info(f"Search returned {len(products)} products for '{query}'")
        else:
            logger.info("Extracting all products from Raley's PDF...")
            products = extract_products_from_pdf(pdf_url)
            logger.info(f"Extraction returned {len(products)} products")
        
        logger.info(f"Total extracted from Raley's PDF: {len(products)} products")
        return products
    except Exception as e:
        logger.error(f"Error extracting offers from Raley's PDF: {e}")
        return []


def fetch_raleys_pdf_circulars(query: str = None, zip_code: str = None, lat: float = None, 
                              lng: float = None, radius_miles: float = 5.0, **kwargs) -> List[Dict]:
    """
    Fetch current Raley's PDF circulars with optional product extraction.
    
    If query is provided:
    - Extracts matching products from PDF using OCR
    - Returns offers with prices and promo text
    
    If query is None:
    - Returns circular metadata for browsing/embedding in app
    
    Args:
        query: Optional product name to search for
        **kwargs: Additional arguments (ignored)
    
    Returns:
        List of offers (product matches or circular metadata)
    """
    offers = []
    
    # Known Raley's PDF URLs for Reno/Nevada area
    raley_pdf_urls = [
        'https://contenthandler-raleys.fieldera.com/prodcoll/35075/0/0/102925_RBN.pdf',
    ]
    
    for pdf_url in raley_pdf_urls:
        logger.info(f"Processing Raley's PDF: {pdf_url}")
        logger.info(f"Query provided: {query}")
        try:
            if not verify_raleys_pdf_url(pdf_url):
                logger.warning(f"Skipping inaccessible Raley's PDF: {pdf_url}")
                continue
            
            # If a query is provided, extract products matching that query
            if query:
                logger.info(f"Extracting products matching '{query}' from Raley's PDF using OCR...")
                products = extract_offers_from_raleys_pdf(pdf_url, query)
                logger.info(f"OCR extraction returned {len(products)} products")
                
                # Convert extracted products to offer format
                for product in products:
                    offers.append({
                        'provider': "Raley's Weekly Ad",
                        'store': "Raley's",
                        'product_name': product.get('name', 'Unknown Product'),
                        'price': product.get('price'),
                        'unit': product.get('unit', 'each'),
                        'url': pdf_url,
                        'promo_text': product.get('promo', ''),
                        'section': product.get('section', 'Featured'),
                        'distance_miles': 2.5,
                    })
                
                if products:
                    logger.info(f"Found {len(products)} matching products from Raley's PDF")
                else:
                    logger.debug(f"No products matching '{query}' found in Raley's PDF")
            
            # Always include circular metadata for browsing
            offers.append({
                'provider': "Raley's Circular (PDF)",
                'store': "Raley's",
                'product_name': 'Weekly Circular',
                'price': None,
                'unit': None,
                'url': pdf_url,
                'promo_text': 'View current weekly ad and promotions',
                'section': 'All Departments',
                'distance_miles': 2.5,
            })
        except Exception as e:
            logger.error(f"Error processing Raley's PDF {pdf_url}: {e}", exc_info=True)
            continue
    
    logger.info(f"Returning {len(offers)} offers from Raley's")
    return offers

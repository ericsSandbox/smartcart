"""
Raley's fetcher using curated product database from circular.
Provides accurate prices and products from the weekly ad.

Can fall back to PaddleOCR-based PDF extraction if enabled.
"""

import logging
import os
from typing import List, Dict, Optional
from .raleys_products_db import search_products

logger = logging.getLogger(__name__)

# Enable PDF extraction fallback via environment variable
ENABLE_PDF_EXTRACTION = os.getenv('RALEY_PDF_EXTRACTION', 'false').lower() == 'true'


def fetch_raleys_from_database(query: Optional[str] = None, **kwargs) -> List[Dict]:
    """
    Fetch Raley's products from curated database.
    
    Args:
        query: Optional product search term
        **kwargs: Additional arguments (ignored)
    
    Returns:
        List of offers in API format
    """
    try:
        if query:
            logger.info(f"[Raley's DB] Searching for '{query}'")
            products = search_products(query)
        else:
            # Return a featured selection
            logger.info("[Raley's DB] Returning featured products")
            from .raleys_products_db import RALEYS_PRODUCTS
            products = []
            for category, items in RALEYS_PRODUCTS.items():
                products.extend(items[:3])  # Top 3 from each category
        
        # Convert to offers format
        offers = []
        for product in products:
            offers.append({
                "provider": "unknown",
                "store": "Raley's",
                "product_name": product.get("name"),
                "price": product.get("price"),
                "unit": product.get("unit", "each"),
                "url": None,
                "promo_text": f"Weekly Ad - {product.get('category', 'Featured')}",
                "distance_miles": 2.5,
            })
        
        logger.info(f"[Raley's DB] Returning {len(offers)} offers for '{query}'")
        return offers
    
    except Exception as e:
        logger.error(f"[Raley's DB] Error: {e}", exc_info=True)
        return []


def fetch_raleys_from_pdf(pdf_path: str, query: Optional[str] = None, **kwargs) -> List[Dict]:
    """
    Extract Raley's products from PDF circular using PaddleOCR.
    
    Args:
        pdf_path: Path to Raley's circular PDF
        query: Optional product search term to filter results
        **kwargs: Additional arguments
    
    Returns:
        List of offers in API format
    """
    try:
        from .intelligent_extractor import extract_raley_circular
        
        logger.info(f"[Raley's PDF] Extracting from {pdf_path}")
        products = extract_raley_circular(pdf_path, method='paddle')
        
        if query:
            logger.info(f"[Raley's PDF] Filtering for '{query}'")
            query_lower = query.lower().replace('-', ' ').split()
            products = [
                p for p in products
                if any(token in p['name'].lower() for token in query_lower)
            ]
        
        # Convert to offers format
        offers = []
        for product in products:
            offers.append({
                "provider": "unknown",
                "store": "Raley's",
                "product_name": product.get("name"),
                "price": product.get("price"),
                "unit": product.get("unit", "each"),
                "url": None,
                "promo_text": "Weekly Ad - PDF Extract",
                "distance_miles": 2.5,
            })
        
        logger.info(f"[Raley's PDF] Returning {len(offers)} offers")
        return offers
    
    except Exception as e:
        logger.error(f"[Raley's PDF] Error: {e}", exc_info=True)
        return []

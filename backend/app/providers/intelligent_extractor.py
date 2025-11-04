"""
Intelligent PDF circular extractor that uses multiple methods.
Prioritizes PaddleOCR for accuracy, falls back to other methods as needed.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_raley_circular(pdf_path: str, method: str = 'auto') -> List[Dict]:
    """
    Extract products from Raley's circular using best available method.
    
    Args:
        pdf_path: Path to PDF circular
        method: 'paddle' (PaddleOCR), 'tesseract', 'auto' (best available)
    
    Returns:
        List of products with names and prices
    """
    pdf_path = str(pdf_path)
    
    if not Path(pdf_path).exists():
        logger.error(f"PDF not found: {pdf_path}")
        return []
    
    logger.info(f"Extracting from {Path(pdf_path).name} using method: {method}")
    
    if method == 'auto':
        # Try PaddleOCR first (better accuracy), fallback to Tesseract
        products = _try_paddle_extraction(pdf_path)
        
        if products:
            logger.info(f"✓ PaddleOCR: Extracted {len(products)} products")
            return products
        
        logger.info("PaddleOCR failed or unavailable, trying Tesseract...")
        products = _try_tesseract_extraction(pdf_path)
        
        if products:
            logger.info(f"✓ Tesseract: Extracted {len(products)} products")
            return products
        
        logger.warning("All extraction methods failed")
        return []
    
    elif method == 'paddle':
        return _try_paddle_extraction(pdf_path)
    
    elif method == 'tesseract':
        return _try_tesseract_extraction(pdf_path)
    
    else:
        logger.error(f"Unknown extraction method: {method}")
        return []


def _try_paddle_extraction(pdf_path: str) -> List[Dict]:
    """Attempt extraction with PaddleOCR."""
    try:
        from app.providers.raleys_paddle_ocr import extract_raleys_paddle
        
        logger.debug("Attempting PaddleOCR extraction...")
        products = extract_raleys_paddle(pdf_path)
        
        if products:
            return products
        else:
            logger.debug("PaddleOCR returned no products")
            return []
    
    except Exception as e:
        logger.debug(f"PaddleOCR extraction failed: {e}")
        return []


def _try_tesseract_extraction(pdf_path: str) -> List[Dict]:
    """Attempt extraction with Tesseract OCR using multiple passes."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        import re
        
        logger.debug("Attempting Tesseract extraction with multiple passes...")
        
        all_products = {}  # Use dict to deduplicate across passes
        
        # Try multiple DPI and PSM settings to catch more items
        extraction_configs = [
            (150, '--psm 6 --oem 3'),  # Default
            (200, '--psm 6 --oem 3'),  # Higher DPI
            (100, '--psm 3 --oem 3'),  # Lower DPI, different PSM
            (150, '--psm 3 --oem 3'),  # Original DPI, different PSM
            (300, '--psm 6 --oem 3'),  # Very high DPI
        ]
        
        for dpi, config in extraction_configs:
            logger.debug(f"  Pass: DPI={dpi}, PSM config={config}")
            
            try:
                images = convert_from_path(pdf_path, dpi=dpi)
                
                for page_num, image in enumerate(images):
                    text = pytesseract.image_to_string(image, config=config)
                    
                    # Parse text to products
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or len(line) < 5:
                            continue
                        
                        price_match = re.search(r'\$?([\d.]+)\s*(?:/\s*(lb|ea|can|box))?', line)
                        
                        if price_match:
                            try:
                                price = float(price_match.group(1))
                                unit = price_match.group(2) or 'ea'
                                product_name = line[:price_match.start()].strip()
                                
                                if product_name and len(product_name) > 3:
                                    # Use product name as key to avoid duplicates
                                    key = product_name.lower().strip()
                                    if key not in all_products:
                                        all_products[key] = {
                                            'name': product_name,
                                            'price': price,
                                            'unit': unit,
                                            'source': 'tesseract'
                                        }
                            except ValueError:
                                continue
            except Exception as e:
                logger.debug(f"  Pass failed: {e}")
                continue
        
        return list(all_products.values())
    
    except Exception as e:
        logger.debug(f"Tesseract extraction failed: {e}")
        return []


def get_extraction_stats(products: List[Dict]) -> Dict:
    """Get statistics about extracted products."""
    if not products:
        return {
            'total': 0,
            'by_unit': {},
            'price_range': (0, 0),
            'avg_price': 0
        }
    
    prices = [p['price'] for p in products]
    units = {}
    
    for p in products:
        unit = p.get('unit', 'ea')
        units[unit] = units.get(unit, 0) + 1
    
    return {
        'total': len(products),
        'by_unit': units,
        'price_range': (min(prices), max(prices)),
        'avg_price': sum(prices) / len(prices),
        'products': products
    }


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python intelligent_extractor.py <pdf_path> [method]")
        print("  method: 'auto' (default), 'paddle', 'tesseract'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else 'auto'
    
    products = extract_raley_circular(pdf_path, method)
    stats = get_extraction_stats(products)
    
    print(f"\n📊 Extraction Results:")
    print(f"  Total products: {stats['total']}")
    print(f"  By unit: {stats['by_unit']}")
    print(f"  Price range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}")
    print(f"  Average price: ${stats['avg_price']:.2f}")
    
    if products:
        print(f"\n  Sample products:")
        for p in products[:10]:
            print(f"    - {p['name']}: ${p['price']}/{p['unit']}")

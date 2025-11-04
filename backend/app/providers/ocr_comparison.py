"""
Comparison utility for OCR extraction methods.
Allows testing PaddleOCR vs Tesseract for quality assessment.
"""

import logging
import sys
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_with_tesseract(pdf_path: str) -> List[Dict]:
    """Extract products using Tesseract OCR."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        logger.error("pdf2image or pytesseract not installed")
        return []
    
    products = []
    
    try:
        logger.info("Converting PDF to images for Tesseract...")
        images = convert_from_path(pdf_path, dpi=150)
        
        for page_num, image in enumerate(images):
            logger.info(f"Running Tesseract on page {page_num + 1}/{len(images)}...")
            
            # Apply some preprocessing for better OCR
            text = pytesseract.image_to_string(
                image,
                config='--psm 6 --oem 3'
            )
            
            # Parse extracted text
            page_products = _parse_text_to_products(text)
            products.extend(page_products)
            logger.info(f"  Found {len(page_products)} products on page {page_num + 1}")
    
    except Exception as e:
        logger.error(f"Tesseract extraction error: {e}")
    
    return products


def extract_with_paddle(pdf_path: str) -> List[Dict]:
    """Extract products using PaddleOCR."""
    try:
        from app.providers.raleys_paddle_ocr import extract_raleys_paddle
        return extract_raleys_paddle(pdf_path)
    except Exception as e:
        logger.error(f"PaddleOCR extraction error: {e}")
        return []


def _parse_text_to_products(text: str) -> List[Dict]:
    """Parse OCR text to extract products and prices."""
    import re
    
    products = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Match price patterns
        price_match = re.search(r'\$?([\d.]+)\s*(?:/\s*(lb|ea|can|box))?', line)
        
        if price_match:
            try:
                price = float(price_match.group(1))
                unit = price_match.group(2) or 'ea'
                product_name = line[:price_match.start()].strip()
                
                if product_name and len(product_name) > 3:
                    products.append({
                        'name': product_name,
                        'price': price,
                        'unit': unit,
                        'source': 'tesseract'
                    })
            except ValueError:
                continue
    
    return products


def compare_extraction_methods(pdf_path: str) -> Dict:
    """
    Compare PaddleOCR vs Tesseract extraction quality.
    
    Args:
        pdf_path: Path to PDF circular
    
    Returns:
        Comparison results with metrics
    """
    logger.info(f"Comparing extraction methods on {Path(pdf_path).name}")
    
    logger.info("\n=== Running PaddleOCR ===")
    paddle_products = extract_with_paddle(pdf_path)
    
    logger.info("\n=== Running Tesseract ===")
    tesseract_products = extract_with_tesseract(pdf_path)
    
    # Calculate metrics
    results = {
        'paddle': {
            'count': len(paddle_products),
            'products': paddle_products[:10],
            'avg_price': sum(p['price'] for p in paddle_products) / len(paddle_products) if paddle_products else 0,
        },
        'tesseract': {
            'count': len(tesseract_products),
            'products': tesseract_products[:10],
            'avg_price': sum(p['price'] for p in tesseract_products) / len(tesseract_products) if tesseract_products else 0,
        }
    }
    
    # Determine winner
    if len(paddle_products) > len(tesseract_products):
        results['winner'] = 'PaddleOCR'
        results['reason'] = f"More products: {len(paddle_products)} vs {len(tesseract_products)}"
    elif len(tesseract_products) > len(paddle_products):
        results['winner'] = 'Tesseract'
        results['reason'] = f"More products: {len(tesseract_products)} vs {len(paddle_products)}"
    else:
        results['winner'] = 'Tie'
        results['reason'] = f"Both found {len(paddle_products)} products"
    
    return results


def print_comparison_report(results: Dict):
    """Print formatted comparison report."""
    print("\n" + "="*70)
    print("OCR EXTRACTION COMPARISON REPORT")
    print("="*70)
    
    print("\n📊 PaddleOCR Results:")
    print(f"  ✓ Products found: {results['paddle']['count']}")
    print(f"  ✓ Average price: ${results['paddle']['avg_price']:.2f}")
    print(f"  Sample products:")
    for p in results['paddle']['products'][:5]:
        print(f"    - {p['name']}: ${p['price']}/{p['unit']}")
    
    print("\n📊 Tesseract Results:")
    print(f"  ✓ Products found: {results['tesseract']['count']}")
    print(f"  ✓ Average price: ${results['tesseract']['avg_price']:.2f}")
    print(f"  Sample products:")
    for p in results['tesseract']['products'][:5]:
        print(f"    - {p['name']}: ${p['price']}/{p['unit']}")
    
    print("\n🏆 Winner: " + results['winner'])
    print(f"  Reason: {results['reason']}")
    print("\n" + "="*70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python ocr_comparison.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)
    
    results = compare_extraction_methods(pdf_path)
    print_comparison_report(results)

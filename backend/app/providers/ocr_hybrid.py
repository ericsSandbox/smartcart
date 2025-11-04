"""
OCR extraction comparison and hybrid approach.

Compares Tesseract OCR vs PaddleOCR for accuracy,
allowing fallback between methods or ensemble results.
"""

import logging
from typing import List, Dict, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class OCRComparator:
    """Compare and combine results from different OCR engines."""
    
    def __init__(self):
        """Initialize OCR engines."""
        self.paddle_available = False
        self.tesseract_available = False
        
        try:
            from .raleys_paddle_ocr import PaddleOCRExtractor
            self.paddle_extractor = PaddleOCRExtractor()
            self.paddle_available = True
            logger.info("PaddleOCR available")
        except Exception as e:
            logger.warning(f"PaddleOCR not available: {e}")
            self.paddle_extractor = None
        
        try:
            from .raleys_pdf import extract_raleys_pdf_with_tesseract
            self.tesseract_available = True
            logger.info("Tesseract available")
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
    
    def extract_with_fallback(self, pdf_path: str) -> List[Dict]:
        """
        Try PaddleOCR first, fallback to Tesseract if it fails.
        
        Args:
            pdf_path: Path to PDF
        
        Returns:
            List of extracted products
        """
        products = []
        
        # Try PaddleOCR first (better accuracy)
        if self.paddle_available:
            try:
                logger.info("Attempting PaddleOCR extraction...")
                products = self.paddle_extractor.extract_from_pdf(pdf_path)
                
                if products:
                    logger.info(f"PaddleOCR: extracted {len(products)} products")
                    return products
                else:
                    logger.warning("PaddleOCR: no products extracted, trying Tesseract...")
            except Exception as e:
                logger.warning(f"PaddleOCR failed: {e}, trying Tesseract...")
        
        # Fallback to Tesseract
        if self.tesseract_available:
            try:
                logger.info("Attempting Tesseract extraction...")
                from .raleys_pdf import extract_raleys_pdf_with_tesseract
                products = extract_raleys_pdf_with_tesseract(pdf_path)
                
                if products:
                    logger.info(f"Tesseract: extracted {len(products)} products")
                    return products
            except Exception as e:
                logger.warning(f"Tesseract also failed: {e}")
        
        logger.error("All OCR methods failed")
        return []
    
    def extract_with_ensemble(self, pdf_path: str) -> List[Dict]:
        """
        Use both OCR engines and combine results, preferring higher confidence.
        
        Args:
            pdf_path: Path to PDF
        
        Returns:
            Combined list of unique products
        """
        all_products = []
        
        # Try both methods
        if self.paddle_available:
            try:
                logger.info("Paddle ensemble extraction...")
                paddle_results = self.paddle_extractor.extract_from_pdf(pdf_path)
                all_products.extend([{**p, "ocr_source": "paddle"} for p in paddle_results])
            except Exception as e:
                logger.warning(f"Paddle ensemble failed: {e}")
        
        if self.tesseract_available:
            try:
                logger.info("Tesseract ensemble extraction...")
                from .raleys_pdf import extract_raleys_pdf_with_tesseract
                tesseract_results = extract_raleys_pdf_with_tesseract(pdf_path)
                all_products.extend([{**p, "ocr_source": "tesseract"} for p in tesseract_results])
            except Exception as e:
                logger.warning(f"Tesseract ensemble failed: {e}")
        
        if not all_products:
            return []
        
        # Deduplicate and merge similar products
        merged = self._merge_similar_products(all_products)
        logger.info(f"Ensemble: {len(all_products)} raw results → {len(merged)} unique products")
        
        return merged
    
    def _merge_similar_products(self, products: List[Dict]) -> List[Dict]:
        """
        Merge products that appear to be the same across OCR methods.
        
        Args:
            products: List of products from multiple sources
        
        Returns:
            Deduplicated list with averaged prices where applicable
        """
        # Group by normalized name
        grouped = {}
        
        for product in products:
            name = product.get("name", "").lower().strip()
            # Normalize: remove extra spaces, common words
            normalized = re.sub(r'\s+', ' ', name)
            
            if normalized not in grouped:
                grouped[normalized] = []
            grouped[normalized].append(product)
        
        # Merge groups
        merged = []
        for normalized_name, group in grouped.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Average price across OCR sources
                prices = [p.get("price") for p in group if p.get("price")]
                avg_price = sum(prices) / len(prices) if prices else None
                
                merged_product = {
                    "name": group[0]["name"],  # Use original formatting from first source
                    "price": avg_price,
                    "unit": group[0].get("unit", "ea"),
                    "store": "Raley's",
                    "sources": [p.get("ocr_source") for p in group],
                    "source": "ensemble_ocr"
                }
                merged.append(merged_product)
        
        return merged


def extract_raleys_hybrid(pdf_path: str, ensemble: bool = False) -> List[Dict]:
    """
    Extract Raley's products using hybrid OCR approach.
    
    Args:
        pdf_path: Path to PDF
        ensemble: If True, use both methods and combine. If False, fallback strategy.
    
    Returns:
        List of extracted products
    """
    comparator = OCRComparator()
    
    if ensemble:
        return comparator.extract_with_ensemble(pdf_path)
    else:
        return comparator.extract_with_fallback(pdf_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ocr_hybrid.py <pdf_path> [--ensemble]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    ensemble_mode = "--ensemble" in sys.argv
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    products = extract_raleys_hybrid(pdf_path, ensemble=ensemble_mode)
    
    print(f"\nExtracted {len(products)} products:\n")
    for product in products[:20]:
        sources = product.get("sources", ["unknown"])
        source_info = f" (from {sources})" if ensemble_mode else ""
        print(f"{product['name']}: ${product['price']}/{product['unit']}{source_info}")
    
    if len(products) > 20:
        print(f"\n... and {len(products) - 20} more")

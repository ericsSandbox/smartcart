"""
Raley's circular extractor using PaddleOCR for improved accuracy.

PaddleOCR provides better accuracy than Tesseract, especially for:
- Low-quality PDF scans
- Unusual text layouts
- Price extraction (numerical accuracy)
- Rotated/skewed text

This module serves as a fallback when PDF structure parsing fails.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)


class PaddleOCRExtractor:
    """Extract products and prices from Raley's circulars using PaddleOCR."""
    
    def __init__(self, language: str = "en"):
        """
        Initialize PaddleOCR extractor.
        
        Args:
            language: OCR language (default: English)
        """
        if PaddleOCR is None:
            raise ImportError("paddleocr is not installed. Install with: pip install paddleocr")
        
        logger.info("Initializing PaddleOCR...")
        self.ocr = PaddleOCR(lang=language)
        logger.info("PaddleOCR initialized")
    
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract products from a Raley's circular PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of products with name and price
        """
        products = []
        
        try:
            pdf_document = fitz.open(pdf_path)
            logger.info(f"Opened PDF: {pdf_path} ({len(pdf_document)} pages)")
            
            for page_num, page in enumerate(pdf_document):
                logger.info(f"Processing page {page_num + 1}/{len(pdf_document)}...")
                
                # Render page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = pix.tobytes("png")
                
                # Save temporarily for OCR
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(img_data)
                    tmp_path = tmp.name
                
                try:
                    # Run OCR on image
                    ocr_results = self.ocr.ocr(tmp_path, cls=True)
                    
                    # Extract text and prices
                    page_products = self._parse_ocr_results(ocr_results)
                    products.extend(page_products)
                    logger.info(f"  Found {len(page_products)} products on page {page_num + 1}")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            
            pdf_document.close()
            
        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}", exc_info=True)
            return []
        
        return products
    
    def _parse_ocr_results(self, ocr_results: List) -> List[Dict]:
        """
        Parse OCR results to extract products and prices.
        
        Args:
            ocr_results: List of OCR detection results
        
        Returns:
            List of product dictionaries
        """
        products = []
        text_blocks = []
        
        if not ocr_results or not ocr_results[0]:
            return products
        
        # Extract all text with confidence scores
        for line in ocr_results[0]:
            if not line:
                continue
            
            bbox, (text, confidence) = line[0], line[1]
            if confidence > 0.5:  # Filter low-confidence detections
                text_blocks.append({
                    "text": text.strip(),
                    "confidence": confidence,
                    "y_pos": bbox[0][1]  # Y position for grouping related items
                })
        
        # Group text blocks by vertical position (items on same horizontal line)
        products = self._group_and_extract_products(text_blocks)
        
        return products
    
    def _group_and_extract_products(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Group text blocks by position and extract product + price pairs.
        
        Args:
            text_blocks: List of OCR text blocks with positions
        
        Returns:
            List of product dictionaries with names and prices
        """
        products = []
        
        # Sort by Y position (top to bottom)
        text_blocks.sort(key=lambda x: x["y_pos"])
        
        # Group blocks that are close vertically (within 20 pixels)
        groups = []
        current_group = []
        last_y = None
        
        for block in text_blocks:
            if last_y is None or abs(block["y_pos"] - last_y) < 20:
                current_group.append(block)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [block]
            last_y = block["y_pos"]
        
        if current_group:
            groups.append(current_group)
        
        # Extract product info from each group
        for group in groups:
            product = self._extract_product_from_group(group)
            if product:
                products.append(product)
        
        return products
    
    def _extract_product_from_group(self, group: List[Dict]) -> Optional[Dict]:
        """
        Extract product name and price from a text group.
        
        Args:
            group: List of text blocks for one product
        
        Returns:
            Product dictionary or None if price not found
        """
        # Combine all text in group
        full_text = " ".join(block["text"] for block in group)
        
        # Extract price (most common pattern: $X.XX or X.XX/unit)
        price_match = re.search(r'\$?([\d.]+)\s*(?:/(\w+))?', full_text)
        
        if not price_match:
            return None
        
        price = float(price_match.group(1))
        unit = price_match.group(2) or "ea"
        
        # Extract product name (text before price)
        price_pos = price_match.start()
        product_name = full_text[:price_pos].strip()
        
        if not product_name or len(product_name) < 3:
            return None
        
        return {
            "name": product_name,
            "price": price,
            "unit": unit,
            "store": "Raley's",
            "source": "paddle_ocr"
        }
    
    def extract_from_directory(self, directory: str) -> List[Dict]:
        """
        Extract products from all PDFs in a directory.
        
        Args:
            directory: Path to directory containing PDFs
        
        Returns:
            List of products from all PDFs
        """
        products = []
        pdf_dir = Path(directory)
        
        for pdf_file in pdf_dir.glob("*.pdf"):
            logger.info(f"Processing {pdf_file.name}...")
            file_products = self.extract_from_pdf(str(pdf_file))
            products.extend(file_products)
        
        return products


def extract_raleys_paddle(pdf_path: str) -> List[Dict]:
    """
    Convenience function to extract Raley's products using PaddleOCR.
    
    Args:
        pdf_path: Path to Raley's circular PDF
    
    Returns:
        List of products with prices
    """
    try:
        extractor = PaddleOCRExtractor()
        return extractor.extract_from_pdf(pdf_path)
    except Exception as e:
        logger.error(f"PaddleOCR extraction failed: {e}")
        return []


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python raleys_paddle_ocr.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    products = extract_raleys_paddle(pdf_path)
    
    print(f"\nExtracted {len(products)} products:\n")
    for product in products[:20]:  # Show first 20
        print(f"{product['name']}: ${product['price']}/{product['unit']}")
    
    if len(products) > 20:
        print(f"\n... and {len(products) - 20} more")

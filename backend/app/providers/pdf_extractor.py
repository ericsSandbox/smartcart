"""
PDF text extraction for grocery store circulars.
Extracts product names, prices, and promotional text from circular PDFs using OCR.
Optimized for performance with caching and page limits.
"""

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re
import logging
import requests
import tempfile
import os
from typing import List, Dict, Optional
from io import BytesIO
from functools import lru_cache
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# Simple in-memory cache for extracted text
_ocr_cache = {}


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Preprocess an image to improve OCR accuracy.
    
    Args:
        image: PIL Image object
    
    Returns:
        Preprocessed image optimized for OCR
    """
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Double the contrast
    
    # Enhance brightness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)  # Slightly brighter
    
    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)
    
    logger.debug(f"Image preprocessed: {image.size}, mode: {image.mode}")
    return image


def extract_text_from_pdf_ocr(pdf_source: str, max_pages: int = None) -> str:
    """
    Extract all text from a PDF file using OCR (Tesseract).
    This handles both text-based and image-based PDFs.
    Includes caching to avoid re-processing the same PDF.
    
    Args:
        pdf_source: Path or URL to PDF file
        max_pages: Maximum pages to extract (defaults to 2 for speed)
    
    Returns:
        Concatenated text from all pages
    """
    # Default to 4 pages for OCR performance  (provides good coverage while staying reasonably fast)
    if max_pages is None:
        max_pages = 4
    
    # Cache key
    cache_key = f"{pdf_source}:pages:{max_pages}"
    if cache_key in _ocr_cache:
        logger.debug(f"Using cached OCR results for {pdf_source}")
        return _ocr_cache[cache_key]
    
    temp_path = None
    try:
        # If it's a URL, download it first to a temp file
        if pdf_source.startswith(('http://', 'https://')):
            logger.debug(f"Downloading PDF from URL: {pdf_source}")
            try:
                response = requests.get(pdf_source, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to download PDF: {e}")
                _ocr_cache[cache_key] = ""
                return ""
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(response.content)
                temp_path = tmp.name
            pdf_file = temp_path
        else:
            pdf_file = pdf_source
        
        # First try pdfplumber for native text extraction (faster than OCR)
        text_parts = []
        try:
            logger.debug(f"Attempting pdfplumber text extraction from {pdf_file}")
            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(max_pages, total_pages)
                
                for i, page in enumerate(pdf.pages[:pages_to_process]):
                    try:
                        extracted = page.extract_text()
                        if extracted and len(extracted.strip()) > 50:  # Only keep substantial text
                            text_parts.append(extracted)
                    except Exception as page_e:
                        logger.debug(f"Error extracting text from page {i+1}: {page_e}")
                        continue
        except Exception as e:
            logger.debug(f"pdfplumber extraction failed, will try OCR: {e}")
        
        # If pdfplumber found substantial text (>200 chars total), return it
        combined_text = "\n\n--- PAGE BREAK ---\n\n".join(text_parts) if text_parts else ""
        if len(combined_text) > 200:
            logger.info(f"Extracted {len(combined_text)} characters using pdfplumber")
            _ocr_cache[cache_key] = combined_text
            return combined_text
        
        # Fall back to OCR for image-based PDFs (very slow, use minimal pages)
        logger.info(f"Using OCR to extract text from {pdf_source} ({max_pages} page limit)")
        try:
            logger.debug("Converting PDF pages to images at ultra-high DPI (600 DPI for best OCR accuracy)...")
            # 600 DPI for maximum OCR accuracy - necessary for poor-quality PDFs
            images = convert_from_path(pdf_file, first_page=1, last_page=max_pages, dpi=600)
            logger.debug(f"Converted {len(images)} pages to images at 600 DPI")
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            _ocr_cache[cache_key] = ""
            return ""
        
        ocr_text_parts = []
        for i, img in enumerate(images):
            try:
                logger.debug(f"Running OCR on page {i+1}/{len(images)}...")
                
                # Preprocess image for better OCR accuracy
                img = preprocess_image_for_ocr(img)
                
                # Run OCR with optimized settings for receipts/circulars
                # PSM modes:
                # 3 = Auto
                # 4 = Single column
                # 5 = Single block
                # 6 = Uniform block of text (best for circulars)
                # 11 = Sparse text
                ocr_text = pytesseract.image_to_string(
                    img,
                    config='--psm 6 --oem 3',  # PSM 6 for structured, OEM 3 for best accuracy
                    timeout=120  # 120 sec timeout per page for high DPI
                )
                
                if ocr_text and len(ocr_text.strip()) > 50:  # Only keep if OCR produced real text
                    logger.debug(f"Page {i+1} OCR produced {len(ocr_text)} characters")
                    ocr_text_parts.append(ocr_text)
                else:
                    logger.debug(f"Page {i+1} OCR produced minimal text: {len(ocr_text) if ocr_text else 0} chars")
            except Exception as page_e:
                logger.warning(f"OCR failed or timed out for page {i+1}: {page_e}")
                continue
        
        result = "\n\n--- PAGE BREAK ---\n\n".join(ocr_text_parts)
        if ocr_text_parts:
            logger.info(f"OCR extracted {len(ocr_text_parts)} pages at 600 DPI ({len(result)} characters total)")
        else:
            logger.warning(f"OCR extraction produced no text from {pdf_source}")
        
        # Cache the result
        _ocr_cache[cache_key] = result
        return result
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_source}: {e}")
        _ocr_cache[cache_key] = ""
        return ""
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


def extract_products_from_text(text: str) -> List[Dict[str, any]]:
    """
    Extract product names and prices from circular text.
    Optimized for OCR-extracted text which may have formatting issues.
    
    Handles OCR artifacts like:
    - Text split across lines
    - Garbled special characters
    - Inconsistent spacing
    
    Looks for patterns like:
    - "PRODUCT NAME $X.XX/unit"
    - "Non-Member Price $X.XX"
    - "PRODUCT NAME Price $X.XX/lb"
    
    Args:
        text: Extracted PDF text (may contain OCR artifacts)
    
    Returns:
        List of product dictionaries with name, price, and promo text
    """
    products = []
    seen = set()
    
    # First, collapse multi-line product entries into single lines
    # This handles OCR artifacts where products are split across lines
    collapsed_text = text
    
    # Replace common OCR splits with spaces
    collapsed_text = collapsed_text.replace('\n', ' ')
    
    # Clean up extra spaces and common OCR artifacts
    collapsed_text = re.sub(r'\s+', ' ', collapsed_text)  # Multiple spaces to single
    collapsed_text = collapsed_text.replace(' . ', '. ')  # Fix ". " spacing
    
    # More relaxed patterns for OCR text
    # Look for: PRODUCT NAME followed by $ price indicator
    price_patterns = [
        # Pattern: "Name $X.XX/lb" or "Name $X.XX ea"
        r'([A-Z][A-Za-z\s\(\)\-\.,&]+?)\s+\$\s*([\d.]+)\s*(?:/\s*([a-z]+))?',
        # Pattern: "Name Price $X.XX"
        r'([A-Z][A-Za-z\s\(\)\-\.,&]+?)\s+(?:Price|price)\s+\$\s*([\d.]+)',
        # Pattern: "Name Non-Member Price $X.XX"
        r'([A-Z][A-Za-z\s\(\)\-\.,&]+?)\s+Non-Member\s+(?:Price|price)\s+\$\s*([\d.]+)',
    ]
    
    for pattern in price_patterns:
        matches = re.finditer(pattern, collapsed_text)
        for match in matches:
            try:
                product_name = match.group(1).strip().rstrip('.,').strip()
                price_str = match.group(2).strip()
                unit = match.group(3).lower() if len(match.groups()) > 2 and match.group(3) else "each"
                
                # Extract price
                price = float(price_str.replace(",", ""))
                
                # Sanity checks
                if price < 0.10 or price > 999 or len(product_name) < 3:
                    continue
                if product_name in seen:
                    continue
                
                # Clean up product name (remove OCR artifacts)
                # Common OCR mangling: "S Raley's" -> "Raley's", extra letters
                product_name = re.sub(r'^[A-Z]\s+', '', product_name)  # Remove leading single letter
                product_name = re.sub(r'\s{2,}', ' ', product_name)  # Multiple spaces
                
                # Skip if empty after cleanup
                if not product_name or len(product_name) < 3:
                    continue
                
                products.append({
                    "name": product_name,
                    "price": price,
                    "unit": unit,
                    "promo": ""
                })
                seen.add(product_name)
                logger.debug(f"Extracted: {product_name} - ${price}/{unit}")
                
            except (ValueError, AttributeError, IndexError) as e:
                logger.debug(f"Error parsing match: {e}")
                continue
    
    logger.info(f"Extracted {len(products)} products from text (saw {len(seen)} unique names)")
    return products


def extract_products_smart(text: str) -> List[Dict[str, any]]:
    """
    Enhanced product extraction using heuristics for grocery circulars.
    Handles OCR-mangled text by being lenient with formatting.
    
    Looks for patterns like:
    - "PRODUCT NAME $X.XX[/unit]"
    - "$X.XX Product Name"
    - Product names with prices on same or adjacent lines
    
    Args:
        text: Extracted PDF text (may be OCR-corrupted)
    
    Returns:
        List of products with name, price, and metadata
    """
    products = []
    
    section_keywords = [
        "meat", "beef", "chicken", "pork", "fish", "seafood", "lamb", "turkey",
        "produce", "vegetables", "fruits", "fresh",
        "dairy", "cheese", "milk", "yogurt", "butter",
        "wine", "beer", "spirits", "alcohol", "beverages",
        "dry goods", "pasta", "bread", "bakery", "grocery",
        "frozen", "deli", "prepared"
    ]
    
    lines = text.split("\n")
    current_section = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        if not line_stripped or len(line_stripped) < 3:
            continue
        
        # Detect section headers
        if len(line_stripped) < 40 and not any(c.isdigit() or '$' in c for c in line_stripped):
            for section in section_keywords:
                if section in line_lower:
                    current_section = section
                    break
        
        # Extract prices using liberal regex - accept various formats
        # This handles OCR errors better
        price_patterns = [
            # "$X.XX Product Name" or "Product Name $X.XX"
            r'\$(\d+[.,]\d{2})',
        ]
        
        for pattern in price_patterns:
            price_matches = re.finditer(pattern, line_stripped)
            for price_match in price_matches:
                price_str = price_match.group(1).replace(',', '.')
                
                try:
                    price = float(price_str)
                    if price < 0.25 or price > 50.00:
                        continue
                except ValueError:
                    continue
                
                # Extract product name - try to get text surrounding the price
                price_start = price_match.start()
                price_end = price_match.end()
                
                # Get text before and after the price
                before_price = line_stripped[:price_start].strip()
                after_price = line_stripped[price_end:].strip()
                
                # Product name is usually before the price, but can be after or both
                product_name = None
                unit = "each"
                
                if before_price and len(before_price) > 3:
                    # Extract product name from before price
                    product_name = before_price
                    # Look for unit info after price
                    if after_price and len(after_price) < 10:
                        unit = after_price.lower().rstrip('.')
                elif after_price and len(after_price) > 3:
                    # Product name after price (unusual but happens with OCR)
                    product_name = after_price
                elif i + 1 < len(lines):
                    # Try to get product name from next line
                    next_line = lines[i + 1].strip()
                    if next_line and not '$' in next_line and len(next_line) > 3 and len(next_line) < 60:
                        product_name = next_line
                
                if not product_name:
                    continue
                
                # Clean up product name - remove common junk from OCR
                product_name = product_name.strip()
                
                # Remove OCR artifacts
                product_name = re.sub(r'[_\-]{2,}', ' ', product_name)  # Remove repeated dashes
                product_name = re.sub(r'\s+', ' ', product_name)  # Collapse whitespace
                
                # Skip known false positives
                false_pos = ["price", "member", "card", "offer", "save", "buy", 
                            "page", "limit", "with", "coupon", "rebate", "promotion",
                            "this week"]
                if any(skip in product_name.lower() for skip in false_pos):
                    continue
                
                # Product name should be at least 4 chars and have letters
                if len(product_name) < 4 or not any(c.isalpha() for c in product_name):
                    continue
                
                # Skip if all numbers or symbols
                if all(not c.isalpha() for c in product_name):
                    continue
                
                products.append({
                    "name": product_name,
                    "price": price,
                    "unit": unit,
                    "section": current_section or "Featured",
                    "promo": "",
                    "original_line": line_stripped
                })
    
    return products


def extract_products_from_pdf(pdf_path: str) -> List[Dict[str, any]]:
    """
    Complete pipeline: extract text from PDF, then extract products.
    Uses OCR as fallback for scanned PDFs.
    
    Args:
        pdf_path: Path or URL to PDF
    
    Returns:
        List of product dictionaries
    """
    try:
        text = extract_text_from_pdf_ocr(pdf_path, max_pages=20)  # Limit to first 20 pages
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return []
        
        products = extract_products_smart(text)
        logger.info(f"Extracted {len(products)} products from PDF")
        
        return products
    except Exception as e:
        logger.error(f"Error in PDF product extraction: {e}")
        return []


def find_product_in_circular(pdf_path: str, query: str) -> List[Dict[str, any]]:
    """
    Find a specific product in a PDF circular by name.
    
    Args:
        pdf_path: Path or URL to PDF
        query: Product name to search for (e.g., "wine", "ground beef")
    
    Returns:
        List of matching products
    """
    products = extract_products_from_pdf(pdf_path)
    query_lower = query.lower()
    
    matches = [
        p for p in products
        if query_lower in p["name"].lower()
    ]
    
    return matches

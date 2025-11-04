"""
Raley's PDF extractor using structured text extraction with layout awareness.
Based on semantic extraction rather than low-quality OCR.
Extracts products organized by category with prices and notes.
"""

import logging
import requests
import re
from typing import List, Dict, Optional, Tuple
from io import BytesIO
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Cache to avoid re-fetching PDFs
_pdf_cache: Dict[str, List[Dict]] = {}


def extract_text_with_layout(pdf_source: str) -> str:
    """
    Extract text from PDF with layout structure preserved.
    First tries pdfplumber, then falls back to PyMuPDF + OCR for image-based PDFs.
    
    Args:
        pdf_source: URL or local path to PDF
    
    Returns:
        Text with layout preserved (categories, headers, groupings)
    """
    try:
        pdf_bytes = None
        
        # Download if URL
        if pdf_source.startswith(('http://', 'https://')):
            logger.info(f"Downloading PDF from {pdf_source}")
            response = requests.get(pdf_source, timeout=30)
            response.raise_for_status()
            pdf_bytes = BytesIO(response.content)
            logger.info(f"Downloaded {len(response.content)} bytes")
        else:
            pdf_bytes = BytesIO(open(pdf_source, 'rb').read())
        
        # Try pdfplumber first (for text-based PDFs)
        full_text = ""
        try:
            pdf_bytes.seek(0)
            with pdfplumber.open(pdf_bytes) as pdf:
                logger.info(f"Trying pdfplumber extraction from {len(pdf.pages)} pages")
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text and len(text.strip()) > 100:
                            full_text += text + "\n\n"
                    except Exception as e:
                        logger.debug(f"Error extracting page {page_num}: {e}")
        except Exception as e:
            logger.debug(f"pdfplumber failed: {e}")
        
        # If we got good text, return it
        if len(full_text) > 500:
            logger.info(f"✓ pdfplumber extracted {len(full_text)} characters")
            return full_text
        
        logger.info("pdfplumber returned insufficient text, trying PyMuPDF + OCR...")
        
        # Fallback to PyMuPDF + OCR for image-based PDFs
        try:
            pdf_bytes.seek(0)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            logger.info(f"Opened PDF with {len(doc)} pages")
            
            full_text = ""
            for page_num in range(min(4, len(doc))):  # Limit to first 4 pages for speed
                try:
                    page = doc[page_num]
                    
                    # Render page to high-DPI image for better OCR
                    logger.debug(f"Rendering page {page_num + 1} to image")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # OCR the image
                    logger.debug(f"Running OCR on page {page_num + 1}")
                    text = pytesseract.image_to_string(img)
                    
                    if text and len(text.strip()) > 50:
                        logger.debug(f"✓ OCR extracted {len(text)} chars from page {page_num + 1}")
                        full_text += text + "\n\n--- PAGE BREAK ---\n\n"
                except Exception as e:
                    logger.warning(f"OCR failed on page {page_num + 1}: {e}")
                    continue
            
            doc.close()
            
            logger.info(f"✓ OCR extracted {len(full_text)} characters total")
            return full_text
        
        except Exception as e:
            logger.error(f"PyMuPDF + OCR failed: {e}", exc_info=True)
            return ""
    
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}", exc_info=True)
        return ""


def find_category_sections(text: str) -> Dict[str, str]:
    """
    Identify category sections in the circular text.
    Looks for headers like "Meat & Seafood", "Produce", etc.
    
    Args:
        text: Full extracted text from PDF
    
    Returns:
        Dictionary mapping category name to category text block
    """
    categories = {}
    
    # Common grocery store category patterns
    category_patterns = [
        r'🥩\s*Meat\s*&\s*Seafood',
        r'🥗\s*Produce',
        r'🧀\s*Deli\s*&\s*Bakery',
        r'🧊\s*Frozen\s*&\s*Refrigerated',
        r'🥫\s*Pantry\s*Essentials',
        r'🥤\s*Beverages',
        r'🍷\s*Wine,\s*Beer\s*&\s*Spirits',
        r'🧼\s*Household\s*&\s*Personal\s*Care',
        # Fallback patterns without emoji
        r'Meat\s*(?:&|and)\s*Seafood',
        r'Produce',
        r'Deli\s*(?:&|and)\s*Bakery',
        r'Frozen\s*(?:&|and)\s*Refrigerated',
        r'Pantry\s*(?:Essentials|Items)',
        r'Beverages',
        r'Wine,\s*Beer\s*(?:&|and)\s*Spirits',
        r'Household\s*(?:&|and)\s*Personal\s*Care',
    ]
    
    # Split text by category headers
    for pattern in category_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            # Extract category name
            category_name = match.group(0).replace('🥩', '').replace('🥗', '').replace('🧀', '').replace('🧊', '').replace('🥫', '').replace('🥤', '').replace('🍷', '').replace('🧼', '').strip()
            
            # Find the section from this header to the next header
            start_pos = match.start()
            
            # Find next category header
            next_match = None
            for next_pattern in category_patterns:
                next_matches = list(re.finditer(next_pattern, text[start_pos+1:], re.IGNORECASE))
                if next_matches:
                    next_pos = start_pos + 1 + next_matches[0].start()
                    if next_match is None or next_pos < next_match:
                        next_match = next_pos
            
            end_pos = next_match if next_match else len(text)
            section_text = text[start_pos:end_pos]
            
            if category_name not in categories:
                categories[category_name] = section_text
    
    logger.info(f"Found {len(categories)} product categories")
    return categories


def extract_products_from_section(section_text: str, category_name: str = "") -> List[Dict[str, any]]:
    """
    Extract individual products from a category section.
    Each product has: name, price, unit, notes.
    
    Args:
        section_text: Text block for one category
        category_name: Name of the category (for context)
    
    Returns:
        List of product dictionaries
    """
    products = []
    
    # Pattern to match product lines: "Product Name\tPrice\tNotes"
    # Or "Product Name  $X.XX/unit  Notes"
    # Or "Product Name  $X.XX ea  Notes"
    
    lines = section_text.split('\n')
    
    for line in lines:
        # Skip empty lines, headers, and table separators
        if not line.strip() or line.strip().startswith('---') or '|' in line[:3]:
            continue
        
        # Skip category headers
        if any(cat_pattern in line for cat_pattern in ['Meat', 'Produce', 'Deli', 'Frozen', 'Pantry', 'Beverages', 'Wine', 'Household']):
            continue
        
        # Look for price patterns
        price_pattern = r'\$\s*([\d]+\.[\d]{2})'
        price_match = re.search(price_pattern, line)
        
        if price_match:
            price = float(price_match.group(1))
            
            # Extract unit (lb, ea, oz, etc.)
            unit_pattern = r'/(lb|oz|ea|each|pound|ml|l)'
            unit_match = re.search(unit_pattern, line, re.IGNORECASE)
            unit = unit_match.group(1).lower() if unit_match else None
            
            # Extract product name (everything before the price)
            price_start = price_match.start()
            product_name = line[:price_start].strip()
            
            # Clean up product name
            product_name = re.sub(r'\t+', ' ', product_name)  # Remove tabs
            product_name = re.sub(r'\s+', ' ', product_name)  # Normalize spaces
            product_name = product_name.strip()
            
            # Extract notes (everything after the price)
            price_end = price_match.end()
            notes = line[price_end:].strip()
            
            # Filter out numeric-only or too-short names
            if product_name and len(product_name) > 3 and not re.match(r'^\d+$', product_name):
                products.append({
                    "name": product_name,
                    "price": price,
                    "unit": unit,
                    "notes": notes,
                    "category": category_name,
                    "store": "Raley's",
                    "source": "circular"
                })
    
    logger.info(f"Extracted {len(products)} products from {category_name}")
    return products


def extract_all_products(text: str) -> List[Dict[str, any]]:
    """
    Extract all products from circular text.
    
    Args:
        text: Full extracted text from PDF
    
    Returns:
        List of all products with metadata
    """
    products = []
    
    # Get category sections
    categories = find_category_sections(text)
    
    # Extract products from each category
    for category_name, section_text in categories.items():
        category_products = extract_products_from_section(section_text, category_name)
        products.extend(category_products)
    
    return products


def search_products_by_query(products: List[Dict], query: str) -> List[Dict]:
    """
    Filter products by search query.
    Uses fuzzy matching to handle variations.
    
    Args:
        products: List of all extracted products
        query: Search query (e.g., "tri-tip", "onions")
    
    Returns:
        Filtered list of matching products
    """
    if not query:
        return products
    
    query_tokens = set(query.lower().split())
    matches = []
    
    for product in products:
        product_name = product.get("name", "").lower()
        product_tokens = set(product_name.split())
        
        # If any token from query is in product name, it's a match
        if query_tokens & product_tokens:
            matches.append(product)
    
    logger.info(f"Found {len(matches)} products matching '{query}'")
    return matches


def fetch_raleys_pdf_structured(query: Optional[str] = None, **kwargs) -> List[Dict]:
    """
    Fetch and extract products from Raley's circular using structured extraction.
    Returns offers in the format expected by the pricing API.
    
    Args:
        query: Optional product name to search for
        **kwargs: Additional arguments (zip_code, lat, lng, etc.)
    
    Returns:
        List of offers with prices in API format
    """
    try:
        # Get PDF URL from backend circulars endpoint
        response = requests.get("http://localhost:8000/pricing/circulars", timeout=10)
        if response.status_code != 200:
            logger.warning("Failed to fetch circulars endpoint")
            return []
        
        circulars = response.json()
        pdf_url = None
        
        for circular in circulars:
            if circular.get("store") == "Raley's" and circular.get("url"):
                pdf_url = circular["url"]
                break
        
        if not pdf_url:
            logger.warning("No Raley's PDF URL found")
            return []
        
        # Check cache
        cache_key = f"{pdf_url}:{query}"
        if cache_key in _pdf_cache:
            logger.info(f"Using cached results for {cache_key}")
            return _pdf_cache[cache_key]
        
        # Extract text with layout
        logger.info(f"Extracting text from {pdf_url}")
        text = extract_text_with_layout(pdf_url)
        
        if not text:
            logger.warning("No text extracted from PDF")
            return []
        
        # Extract all products
        products = extract_all_products(text)
        
        # Filter by query if provided
        if query:
            products = search_products_by_query(products, query)
        
        # Convert products to offers format
        offers = []
        for product in products:
            offers.append({
                "provider": "unknown",
                "store": product.get("store", "Raley's"),
                "product_name": product.get("name"),
                "price": product.get("price"),
                "unit": product.get("unit", "each"),
                "url": pdf_url,
                "promo_text": product.get("notes", ""),
                "distance_miles": 2.5,
            })
        
        # Cache results
        _pdf_cache[cache_key] = offers
        
        logger.info(f"Returning {len(offers)} offers")
        return offers
    
    except Exception as e:
        logger.error(f"Error extracting from PDF: {e}", exc_info=True)
        return []

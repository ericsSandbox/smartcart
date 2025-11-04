#!/usr/bin/env python
"""
SaveMart extractor - process PDF in batches to avoid image size limits.
Extract products from 2-3 pages at a time for better quality.
"""

import sys
import os
import json
import base64
from pathlib import Path
from PIL import Image, ImageEnhance
from io import BytesIO

sys.path.insert(0, '/code')

from datetime import date
from app.database import SessionLocal
from app.models import CircularItem
import google.generativeai as genai
import fitz  # PyMuPDF


def pdf_pages_to_image(pdf_path: str, start_page: int, end_page: int, scale_factor: float = 0.8) -> bytes:
    """Convert specific PDF pages into one stitched image."""
    try:
        pdf_document = fitz.open(pdf_path)
        
        images = []
        max_width = 0
        total_height = 0
        
        # Render specified pages to PIL images
        for page_num in range(start_page, min(end_page + 1, len(pdf_document))):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img_bytes = pix.tobytes("ppm")
            img = Image.open(BytesIO(img_bytes))
            
            # Scale down the image
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            images.append(img)
            
            max_width = max(max_width, img.width)
            total_height += img.height
        
        pdf_document.close()
        
        # Create stitched image
        stitched = Image.new('RGB', (max_width, total_height), 'white')
        
        y_offset = 0
        for img in images:
            stitched.paste(img, (0, y_offset))
            y_offset += img.height
        
        # Enhance: moderate contrast and sharpness
        stitched = stitched.convert('L')  # Convert to grayscale
        
        contrast_enhancer = ImageEnhance.Contrast(stitched)
        stitched = contrast_enhancer.enhance(1.5)
        
        sharpener = ImageEnhance.Sharpness(stitched)
        stitched = sharpener.enhance(2.0)
        
        # Convert to JPEG
        jpeg_buffer = BytesIO()
        stitched.save(jpeg_buffer, format='JPEG', quality=95, optimize=True)
        jpeg_bytes = jpeg_buffer.getvalue()
        
        return jpeg_bytes
    
    except Exception as e:
        print(f"❌ Error stitching pages {start_page}-{end_page}: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_with_gemini(image_bytes: bytes, batch_num: int) -> list:
    """Send batch image to Gemini and extract products."""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("  ❌ GOOGLE_API_KEY not set")
        return []
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print(f"  🤖 Sending batch {batch_num} to Gemini...")
    
    system_prompt = """You are an expert at reading grocery store circulars and extracting product pricing and discount information.

Your task: Extract EVERY product shown on these pages with their pricing and discount information.

For each product, extract:
- Product name (exactly as shown)
- Sale price (if showing $X.XX) OR discount percentage (if showing "50% OFF")
- Unit/size
- Category

Return ONLY a JSON array:
[
  {"name": "product name", "price": 5.99, "regular_price": null, "discount_percent": null, "unit": "lb", "category": "Meat & Seafood"},
  {"name": "item", "price": null, "regular_price": null, "discount_percent": 50, "unit": "ea", "category": "Produce"},
]

Categories: Meat & Seafood, Produce, Bakery & Deli, Frozen & Refrigerated, Pantry Essentials, Beverages, Wine/Beer/Spirits, Household & Personal Care, Health & Beauty

IMPORTANT:
- Extract EVERY visible product
- If "50% OFF": discount_percent=50, price=null
- If price shown: price=X.XX, discount_percent=null
- Return ONLY JSON - no markdown"""
    
    user_message = "Extract ALL products shown on this/these page(s). Include sale prices and discount percentages. Return ONLY JSON array."
    
    try:
        response = model.generate_content(
            [
                system_prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": base64.standard_b64encode(image_bytes).decode('utf-8'),
                },
                user_message
            ],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.1,
            )
        )
        
        response_text = response.text.strip()
        
        # Parse JSON
        if "[" not in response_text or "]" not in response_text:
            print(f"    ⚠️ No JSON in response")
            return []
        
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        json_str = response_text[start:end]
        
        products = json.loads(json_str)
        print(f"    ✓ Extracted {len(products)} products from batch {batch_num}")
        
        return products
    
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return []


def seed_to_database(products: list) -> int:
    """Save products to database."""
    db = SessionLocal()
    
    try:
        # Deduplicate
        seen = set()
        unique_products = []
        for p in products:
            key = p.get('name', '').lower().strip()
            if key and key not in seen:
                seen.add(key)
                unique_products.append(p)
        
        # Insert
        items_created = 0
        
        for product in unique_products:
            item_name = product.get('name', '').strip()
            price = product.get('price')
            regular_price = product.get('regular_price')
            discount_percent = product.get('discount_percent')
            unit = product.get('unit', 'ea') or 'ea'
            category = product.get('category', 'Other')
            
            if not item_name:
                continue
            
            # Handle prices
            try:
                if isinstance(price, str):
                    price = float(price.replace('$', '').replace(',', '').strip())
                else:
                    price = float(price) if price else None
            except (ValueError, TypeError):
                price = None
            
            try:
                if isinstance(regular_price, str):
                    regular_price = float(regular_price.replace('$', '').replace(',', '').strip())
                else:
                    regular_price = float(regular_price) if regular_price else None
            except (ValueError, TypeError):
                regular_price = None
            
            try:
                discount_percent = float(discount_percent) if discount_percent else None
            except (ValueError, TypeError):
                discount_percent = None
            
            # Skip if no pricing info
            if price is None and discount_percent is None:
                continue
            
            # Check for duplicates in DB
            existing = db.query(CircularItem).filter(
                CircularItem.retailer == "SaveMart",
                CircularItem.item_name.ilike(item_name)
            ).first()
            
            if existing:
                continue
            
            item = CircularItem(
                retailer="SaveMart",
                item_name=item_name,
                price=price,
                regular_price=regular_price,
                discount_percent=discount_percent,
                unit=unit,
                category=category,
                source='gemini',
                valid_from=date(2025, 10, 29),
                valid_until=date(2025, 11, 4),
            )
            db.add(item)
            items_created += 1
        
        db.commit()
        return items_created
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 0
    
    finally:
        db.close()


if __name__ == "__main__":
    pdf_path = "/code/data/circulars/savemart_weekly.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("SaveMart Extraction - Batch Processing (3 pages at a time)")
    print("=" * 80)
    
    # Get PDF page count
    pdf_doc = fitz.open(pdf_path)
    num_pages = len(pdf_doc)
    pdf_doc.close()
    
    print(f"\n📄 Processing {num_pages} pages in batches of 3...\n")
    
    all_products = []
    batch_num = 1
    
    # Process 3 pages at a time
    for start_page in range(0, num_pages, 3):
        end_page = min(start_page + 2, num_pages - 1)
        page_range = f"Pages {start_page+1}-{end_page+1}"
        
        print(f"📋 Batch {batch_num} ({page_range}):")
        
        image_bytes = pdf_pages_to_image(pdf_path, start_page, end_page, scale_factor=0.8)
        if not image_bytes:
            print(f"  ⚠️ Skipping batch {batch_num}")
            batch_num += 1
            continue
        
        print(f"  Image size: {len(image_bytes) / 1024:.1f} KB")
        
        products = extract_with_gemini(image_bytes, batch_num)
        all_products.extend(products)
        batch_num += 1
    
    print(f"\n💾 Saving to database...")
    print(f"Total extracted: {len(all_products)} products")
    
    # Clear existing
    db = SessionLocal()
    count = db.query(CircularItem).filter(CircularItem.retailer == "SaveMart").delete()
    db.commit()
    db.close()
    print(f"✓ Cleared {count} existing SaveMart items")
    
    # Seed database
    items_created = seed_to_database(all_products)
    
    # Summary
    print("\n" + "=" * 80)
    if items_created > 0:
        print(f"✅ SUCCESS: Extracted and saved {items_created} SaveMart products")
        print("=" * 80)
        sys.exit(0)
    else:
        print("❌ No items saved")
        print("=" * 80)
        sys.exit(1)

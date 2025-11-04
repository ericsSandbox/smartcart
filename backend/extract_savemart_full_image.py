#!/usr/bin/env python
"""
SaveMart extractor - stitch all PDF pages into one image and send to Gemini.
Single request for all products = avoids rate limits + better context.
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


def pdf_to_stitched_image(pdf_path: str, scale_factor: float = 0.7) -> bytes:
    """Convert all PDF pages into one tall stitched image, scaled down by scale_factor (30% smaller = 0.7)."""
    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = len(pdf_document)
        
        print(f"Converting {num_pages} PDF pages to one stitched image (scaled to {int(scale_factor*100)}%)...")
        
        images = []
        max_width = 0
        total_height = 0
        
        # Render all pages to PIL images
        for page_num in range(num_pages):
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
            
            if (page_num + 1) % 5 == 0:
                print(f"  ✓ {page_num + 1}/{num_pages}")
        
        pdf_document.close()
        
        # Create stitched image
        print("Stitching pages together...")
        stitched = Image.new('RGB', (max_width, total_height), 'white')
        
        y_offset = 0
        for img in images:
            stitched.paste(img, (0, y_offset))
            y_offset += img.height
        
        # Enhance: moderate contrast and sharpness for readability
        print("Enhancing image: moderate contrast and sharpness...")
        stitched = stitched.convert('L')  # Convert to grayscale (but keep grays)
        
        # Moderate contrast increase
        contrast_enhancer = ImageEnhance.Contrast(stitched)
        stitched = contrast_enhancer.enhance(1.5)  # 50% contrast boost
        
        # Moderate sharpening
        sharpener = ImageEnhance.Sharpness(stitched)
        stitched = sharpener.enhance(2.0)  # 2x sharpening
        
        # Save to file for inspection
        output_path = "/code/data/circulars/savemart_stitched_preview.jpg"
        stitched.save(output_path, quality=95)
        print(f"✓ Saved preview to: {output_path}")
        
        # Convert to JPEG for API
        print(f"Stitched image: {max_width}x{total_height}px")
        
        jpeg_buffer = BytesIO()
        stitched.save(jpeg_buffer, format='JPEG', quality=95, optimize=True)
        jpeg_bytes = jpeg_buffer.getvalue()
        
        print(f"Final JPEG size: {len(jpeg_bytes) / (1024*1024):.1f} MB")
        return jpeg_bytes
    
    except Exception as e:
        print(f"❌ Error stitching PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_with_gemini_single_image(image_bytes: bytes) -> list:
    """Send one stitched image to Gemini and extract all products."""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("  ❌ GOOGLE_API_KEY not set")
        return []
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print("🤖 Sending full flyer to Gemini...")
    
    system_prompt = """You are an expert at reading grocery store circulars and extracting product pricing and discount information.

Your task: Extract EVERY product advertised in this entire circular - both discounted items AND regular-priced items.

Extract ALL products you can see, including:
- Items with "% OFF" discount badges (set discount_percent field)
- Regular sale prices (set price field)
- Bulk deals and multi-packs (calculate unit price)
- Loyalty program prices
- Items in ALL sections: Meat & Seafood, Produce, Bakery & Deli, Frozen, Pantry, Beverages, Household, Health & Beauty
- Small items in sidebars or corners

For each product, extract:
- Product name (exactly as shown)
- SALE PRICE: If showing a sale price ($X.XX), use that
- DISCOUNT: If showing "50% OFF" or similar badge, set discount_percent (and regular_price if visible)
- Unit/size
- Category

Return ONLY a JSON array with this exact format - NO other text:
[
  {"name": "Beef Tri-Tip Roast", "price": 5.99, "regular_price": null, "discount_percent": null, "unit": "lb", "category": "Meat & Seafood"},
  {"name": "Avocados", "price": null, "regular_price": null, "discount_percent": 50, "unit": "ea", "category": "Produce"},
  {"name": "Cookies", "price": 2.99, "regular_price": 3.99, "discount_percent": null, "unit": "ea", "category": "Bakery & Deli"},
]

Categories: Meat & Seafood, Produce, Bakery & Deli, Frozen & Refrigerated, Pantry Essentials, Beverages, Wine/Beer/Spirits, Household & Personal Care, Health & Beauty, Baby Products, Pharmacy

CRITICAL REMINDERS:
- Extract EVERY visible product, including ones you might think are just headers or promotions
- Look carefully at every column, row, and section
- Include products shown with images, prices, or discount badges
- If discount badge (50% OFF), set discount_percent=50, price=null
- If regular sale price shown, set price=X.XX, discount_percent=null
- Prices MUST be numeric: 4.99 not "$4.99"
- Return ONLY JSON array - no markdown, no explanations"""
    
    user_message = "Extract EVERY product in this entire circular. Include both items with discount badges (50% OFF) AND regular-priced items. Be thorough - look at every section, column, and item. There are likely 50-100+ total products. Return ONLY JSON array."
    
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
        
        # Debug: print raw response
        print(f"\n  Raw Gemini response (first 500 chars):\n{response_text[:500]}\n")
        
        # Parse JSON
        if "[" not in response_text or "]" not in response_text:
            print(f"  ⚠️ No JSON in response")
            return []
        
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        json_str = response_text[start:end]
        
        products = json.loads(json_str)
        print(f"  ✓ Extracted {len(products)} products")
        
        # Debug: print first few products
        print(f"  Sample: {products[:2] if products else 'none'}")
        
        return products
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
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
        
        print(f"✓ Deduplicated to {len(unique_products)} unique products")
        
        # Debug: print extracted products
        print("\nExtracted products (before filtering):")
        for p in unique_products:
            print(f"  - {p.get('name', 'N/A')}: ${p.get('price', 'N/A')} ({type(p.get('price')).__name__})")
        
        # Clear existing
        count = db.query(CircularItem).filter(CircularItem.retailer == "SaveMart").delete()
        print(f"\n✓ Cleared {count} existing SaveMart items")
        
        # Insert
        items_created = 0
        
        for product in unique_products:
            item_name = product.get('name', '').strip()
            price = product.get('price')
            regular_price = product.get('regular_price')
            discount_percent = product.get('discount_percent')
            unit = product.get('unit', 'ea') or 'ea'
            unit = str(unit).strip() if unit else 'ea'
            category = product.get('category', 'Other')
            
            if not item_name:
                continue
            
            # Handle price - convert string if needed
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
            
            # Skip items with no pricing info at all
            if price is None and discount_percent is None:
                print(f"  ⚠️ Skipping {item_name} (no price or discount info)")
                continue
            
            # Display what we're adding
            if price and discount_percent:
                display = f"{item_name} @ ${price:.2f} ({discount_percent:.0f}% OFF)"
            elif price:
                display = f"{item_name} @ ${price:.2f}"
            elif discount_percent:
                if regular_price:
                    display = f"{item_name}: {discount_percent:.0f}% OFF (was ${regular_price:.2f})"
                else:
                    display = f"{item_name}: {discount_percent:.0f}% OFF"
            else:
                display = f"{item_name}"
            
            print(f"  ✓ Adding {display}")
            
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
            
            if items_created % 10 == 0:
                print(f"    {items_created} items...")
        
        db.commit()
        print(f"\n✅ Successfully seeded {items_created} SaveMart items")
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
    print("SaveMart Extraction - Full Flyer as Single Image")
    print("=" * 80)
    
    # Stitch PDF pages
    print("\n📄 Step 1: Stitch all PDF pages into one image...")
    image_bytes = pdf_to_stitched_image(pdf_path, scale_factor=0.8)  # 80% of original (20% smaller)
    
    if not image_bytes:
        print("❌ Failed to create stitched image")
        sys.exit(1)
    
    # Extract with Gemini
    print("\n🤖 Step 2: Extract products from stitched image...")
    products = extract_with_gemini_single_image(image_bytes)
    
    if not products:
        print("❌ No products extracted")
        sys.exit(1)
    
    # Seed database
    print("\n💾 Step 3: Save to database...")
    items_created = seed_to_database(products)
    
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

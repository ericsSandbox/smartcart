# SaveMart Extraction Guide

## Active Extraction Scripts

### 1. **extract_savemart_batches.py** (Primary - Recommended)
- **Location**: `backend/extract_savemart_batches.py`
- **Method**: Batch processing (3 pages at a time)
- **Advantages**:
  - Better detail preservation (smaller images = better Gemini reading)
  - Extracts both discounted (50% OFF) and regular-priced items
  - Handles price and discount information separately
  - ~15-20 products typically extracted
- **Run**: `docker exec -e GOOGLE_API_KEY="..." smartcart-backend-1 timeout 180 python /code/extract_savemart_batches.py`

### 2. **extract_savemart_full_image.py** (Alternative)
- **Location**: `backend/extract_savemart_full_image.py`
- **Method**: Single stitched image (all 18 pages)
- **Advantages**:
  - One API request (avoids rate limits)
  - Entire flyer context at once
- **Disadvantages**:
  - Larger image = potential for fewer products detected
  - Only hits 15 requests/minute rate limit once
- **Run**: `docker exec -e GOOGLE_API_KEY="..." smartcart-backend-1 timeout 120 python /code/extract_savemart_full_image.py`

## Data Processing

### Product Name Sanitization
When adding items from Ad Circulars to shopping lists, product names are automatically cleaned:
- `"Beef Tri-Tip (2 1/2 pound)"` → `"Beef Tri-Tip"`
- `"Cookies or Large Muffins"` → `"Cookies"`
- `"Product Maxx Pack"` → `"Product"`

See: `frontend/src/components/AdCirculars.jsx` - `sanitizeProductName()` function

### Database Schema
- `price` (float, nullable): Sale price
- `regular_price` (float, nullable): Original price before discount
- `discount_percent` (float, nullable): Discount percentage (e.g., 50 for "50% OFF")

## Frontend Display
- Discounted items show red "50% OFF" badges
- Regular prices shown with $ symbol
- Supports both pricing models seamlessly

## API Credentials
- Google Gemini API: Free tier (15 requests/minute)
- No paid subscription required
- Set via `GOOGLE_API_KEY` environment variable

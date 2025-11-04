# Real Grocery Pricing via Weekly Ads

## The Smart Approach

Instead of scraping live inventory (which gets blocked), we scrape **weekly ad circulars** and sale pages. This is brilliant because:

✅ **Stores WANT you to see ads** - No bot protection, public data  
✅ **Weekly refresh cycle** - Don't need real-time data  
✅ **Contains actual sale prices** - The deals customers care about  
✅ **Covers major chains** - Walmart, Safeway, Kroger, etc. all publish weekly ads  
✅ **Easier to parse** - Structured sale pages, not complex inventory systems  

## Current Implementation

### Supported Stores (Reno/89503)
- **Walmart** - Rollback deals page
- **Safeway** - Weekly ad deals
- **Raley's** - Coming soon
- **Smith's** (Kroger) - Coming soon
- **Whole Foods** - Coming soon  
- **Sprouts** - Coming soon
- **Trader Joe's** - Coming soon

### How It Works

1. **User searches for "sugar"**
2. **Backend normalizes**: "2 cups sugar" → "sugar"
3. **Weekly ad scrapers run**:
   - Load Walmart's rollback/deals page
   - Load Safeway's weekly ad
   - Search for "sugar" in each
   - Extract product names and sale prices
4. **Results merged and sorted** by price
5. **Frontend displays**: "Safeway: C&H Sugar 4lb $2.19 (Weekly Ad)"

### Architecture

```
backend/app/providers/
├── scraper_base.py       # Base utilities (HTML fetch, price extraction)
├── weekly_ads.py          # Main weekly ad aggregator
├── walmart.py             # Live inventory (blocked, but tries)
├── savemart.py            # Live inventory (blocked, but tries)
└── utils.py               # Normalization, demo data
```

**Pricing Router Priority**:
1. Weekly ads (most reliable) ← **This is the winner**
2. Live inventory scrapers (likely blocked)
3. Paid APIs (if keys present)
4. Demo mode (fallback for development)

## Adding More Stores

### For Reno Area

**Smith's (Kroger)**:
- Weekly ad: https://www.smithsfoodanddrug.com/weeklyad
- Digital circular with product cards
- JSON data embedded in page

**Raley's**:
- Weekly ad: https://www.raleys.com/weekly-ads
- PDF circular + web version
- May need PDF parsing

**Whole Foods**:
- Sale items: https://www.wholefoodsmarket.com/sales-flyer
- Typically organized by category
- Region-specific deals

**Sprouts**:
- Weekly ad: https://www.sprouts.com/weekly-ad
- Clean HTML structure
- Easy to scrape

**Trader Joe's**:
- No traditional weekly ad
- "Fearless Flyer" seasonal items
- Could scrape https://www.traderjoes.com/home/discover/fearless-flyer

### Implementation Template

```python
class StoreWeeklyAdScraper(GroceryScraper):
    def __init__(self):
        super().__init__('Store Name', 'https://store.com')
    
    def search(self, query, zip_code=None, lat=None, lng=None, radius_miles=5.0):
        offers = []
        
        # Load weekly ad page
        soup = self.fetch_html(f"{self.base_url}/weekly-ad")
        if not soup:
            return offers
        
        query_lower = query.lower()
        
        # Find product cards containing our search term
        for card in soup.find_all('div', class_='product-card'):
            if query_lower not in card.get_text().lower():
                continue
            
            name = card.find('h3').get_text(strip=True)
            price = self.extract_price(card.find('span', class_='price').get_text())
            
            offers.append({
                'provider': 'Store Weekly Ad',
                'store': 'Store Name',
                'price': price,
                'unit': None,
                'url': None,
                'promo_text': 'Weekly Ad',
                'distance_miles': None,
                'product_name': name,
            })
        
        return offers
```

Then add to `weekly_ads.py`:
```python
scrapers = [
    ('Walmart', fetch_walmart_weekly),
    ('Safeway', fetch_safeway_weekly),
    ('Store Name', fetch_store_weekly),  # ← Add here
]
```

## Testing

```bash
# Test weekly ad scrapers
docker-compose exec backend python -c "
from app.providers import weekly_ads
offers = weekly_ads.fetch_all_weekly_ads('sugar', zip_code='89503')
print(f'Found {len(offers)} offers')
for o in offers:
    print(f'  {o[\"store\"]}: {o[\"product_name\"]} - \${o[\"price\"]}')
"
```

## Future Enhancements

### 1. PDF Circular Parsing
Many stores publish PDF circulars. We can parse these with:
```bash
pip install PyPDF2 pdfplumber
```

Extract text, find prices, match to queries.

### 2. Weekly Cache
Since ads change weekly, cache results:
- Store in DB with `store_name`, `week_start_date`, `product_data`
- Refresh Sunday night when new ads drop
- Instant responses, no repeated scraping

### 3. Location Filtering
Some stores show different ads by region:
- Use zip code to determine region
- Load correct ad for that area
- Return distance to nearest store location

### 4. Brand Matching
Weekly ads often show specific brands:
- "Folgers Coffee $5.99"
- Match user query "coffee" to brand items
- Show all coffee brands on sale

## Why This Works

**Weekly ads are public marketing**:
- Stores spend money to advertise these deals
- They WANT maximum visibility
- No login required, no rate limits
- Stable page structures (change weekly, not hourly)
- Perfect for price comparison apps

**vs. Live Inventory Scraping**:
- ❌ Bot protection (CAPTCHAs)
- ❌ Requires login
- ❌ Rate limited
- ❌ Constantly changing page structure
- ❌ Legal gray area

**Weekly ads = win-win**:
- ✅ Stores get ad views
- ✅ Users find best deals
- ✅ No technical barriers
- ✅ Completely legal (public data)

## Current Status

**Working**: Framework is live, Walmart/Safeway scrapers implemented  
**Next**: Add Raley's, Smith's, Sprouts for Reno area  
**Then**: Weekly cache + PDF parsing for holdouts  

Test it now in the app—search for common items and you should see weekly ad offers!

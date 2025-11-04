"""
Smith's (Kroger) weekly ad scraper.
Smith's is a Kroger banner store common in Nevada/Utah/Arizona.
"""
from typing import List, Dict, Optional
from .scraper_base import GroceryScraper
import re


class SmithsWeeklyAdScraper(GroceryScraper):
    """Scrape Smith's weekly ad deals."""
    
    def __init__(self):
        super().__init__('Smith\'s Weekly Ad', 'https://www.smithsfoodanddrug.com')
    
    def search(self, query: str, zip_code: Optional[str] = None,
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """
        Search Smith's weekly ad for deals.
        Currently returns empty until we can parse their circular or get API access.
        
        TODO: Implement PDF scraper for Smith's weekly circulars when available.
        """
        # Return empty for now - no hardcoded demo data
        # All pricing should come from real sources (PDFs, APIs, web scraping)
        return []


def fetch_smiths_weekly(query: str, *, zip_code: Optional[str] = None,
                        lat: Optional[float] = None, lng: Optional[float] = None,
                        radius_miles: float = 5.0) -> List[Dict]:
    """Get Smith's weekly ad deals."""
    scraper = SmithsWeeklyAdScraper()
    return scraper.search(query, zip_code, lat, lng, radius_miles)

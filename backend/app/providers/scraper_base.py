"""
Generic grocery store web scraper base class.
Provides common utilities for parsing store websites.
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


class GroceryScraper:
    """Base scraper with utilities for common grocery site patterns."""
    
    def __init__(self, store_name: str, base_url: str):
        self.store_name = store_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def fetch_html(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML from a URL."""
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, 'lxml')
        except Exception as e:
            print(f"[{self.store_name}] Failed to fetch {url}: {e}")
            return None
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text like '$2.99', '2.99', '$1.49 ea'."""
        if not text:
            return None
        # Remove common suffixes
        text = re.sub(r'\s*(ea|each|lb|per lb|/lb|oz)\s*$', '', text, flags=re.IGNORECASE)
        # Find price pattern
        match = re.search(r'\$?\s*(\d+\.\d{2})', text)
        if match:
            return float(match.group(1))
        # Try integer price
        match = re.search(r'\$?\s*(\d+)', text)
        if match:
            return float(match.group(1))
        return None
    
    def search(self, query: str, zip_code: Optional[str] = None, 
               lat: Optional[float] = None, lng: Optional[float] = None,
               radius_miles: float = 5.0) -> List[Dict]:
        """
        Search the store and return a list of offers.
        Each subclass must implement this.
        
        Returns:
            List of dicts with keys: provider, store, price, unit, url, promo_text, distance_miles
        """
        raise NotImplementedError("Subclass must implement search()")

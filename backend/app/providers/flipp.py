import os
from typing import List, Dict, Optional

# Placeholder implementation. Integrate real Flipp API if you have keys.
# Returns a list of offer dicts with standard keys.

def fetch_offers(query: str, *, zip_code: Optional[str] = None, lat: Optional[float] = None,
                 lng: Optional[float] = None, radius_miles: float = 5.0) -> List[Dict]:
    api_key = os.getenv('FLIPP_API_KEY')
    # If no API key configured, return empty to avoid errors
    if not api_key:
        return []
    # TODO: Implement actual HTTP calls to Flipp with api_key and location.
    # Normalize output as below. For now, return empty to avoid fake data misleading users.
    return []

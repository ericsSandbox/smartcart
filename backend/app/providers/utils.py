import re
import unicodedata

def normalize_ingredient_query(ingredient_name: str) -> str:
    """
    Extract the core ingredient from a full ingredient string.
    Keeps only the essential product name, strips everything else.
    
    Examples:
        "2 tablespoons white sugar" -> "sugar"
        "1 pound lean ground beef" -> "ground beef"
        "3 cups all-purpose flour" -> "flour"
        "jumbo shrimp (21 to 25 count), peeled and deveined, tails off" -> "shrimp"
        "unsalted butter, cut into 4 pieces" -> "butter"
        "sprigs thyme" -> "thyme"
        "cloves garlic, crushed and cut in half" -> "garlic"
        "olive oil" -> "olive oil"
    """
    # Lowercase and strip accents (e.g., jalapeño -> jalapeno)
    lowered = ingredient_name.lower().strip()
    text = unicodedata.normalize('NFKD', lowered).encode('ascii', 'ignore').decode('ascii')
    
    # Remove content inside parentheses (package sizes, counts, etc.)
    text = re.sub(r"\([^)]*\)", " ", text)
    
    # Remove everything after commas (descriptors, preparation notes)
    text = text.split(',')[0].strip()
    
    # Remove quantities at the start (numbers, fractions)
    text = re.sub(r'^\d+(\.\d+)?(/\d+)?(\s+\d+/\d+)?\s*', '', text)
    
    # Remove common units
    units = [
        'tablespoons?', 'tbsp\.?', 'teaspoons?', 'tsp\.?',
        'cups?', 'c\.?', 'ounces?', 'oz\.?', 'pounds?', 'lbs?\.?', 'lb\.?',
        'grams?', 'g\.?', 'kilograms?', 'kg\.?',
        'milliliters?', 'ml\.?', 'liters?', 'l\.?',
        'quarts?', 'qt\.?', 'pints?', 'pt\.?', 'gallons?', 'gal\.?',
        'cloves?', 'pinch(es)?', 'dash(es)?', 'sprig(s)?',
        'cans?', 'packages?', 'package', 'pkg\.?', 'containers?',
        'slices?', 'pieces?', 'whole',
    ]
    
    for unit in units:
        text = re.sub(r'\b' + unit + r'\b', '', text, flags=re.IGNORECASE)
    
    # Remove size adjectives that aren't part of the product name (small, medium, large)
    # but keep them for now to check later
    text = re.sub(r'\b(medium|large|small|extra|jumbo)\s+', '', text, flags=re.IGNORECASE)
    
    # Remove quality/color adjectives before main ingredient (all-purpose, white, brown, lean, etc.)
    adjectives_before = [
        'white', 'brown', 'granulated', 'powdered', 'confectioners?',
        'all-purpose', 'whole wheat', 'bread', 'cake',
        'lean', 'extra', 'unsalted', 'salted',
        'active', 'instant', 'dry',
    ]
    
    for adj in adjectives_before:
        text = re.sub(r'\b' + adj + r'\s+', '', text, flags=re.IGNORECASE)
    
    # Remove descriptive words that follow the ingredient (preparation methods, textures)
    # These come AFTER the ingredient name, so remove them
    descriptors_after = [
        'crushed?', 'cut', 'chopped?', 'diced?', 'sliced?',
        'minced?', 'shredded?', 'grated?', 'peeled?',
        'deveined?', 'skinless', 'boneless', 'trimmed?',
        'and', 'tails?', 'off',
    ]
    
    for desc in descriptors_after:
        text = re.sub(r'\s+' + desc + r'(\s|$)', ' ', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # If we ended up with nothing, return original
    if not text:
        return ingredient_name.strip()
    
    # Normalize common variants to base forms
    variants = {
        'hamburger meat': 'ground beef',
        'hamburger': 'ground beef',
        'minced beef': 'ground beef',
        'ground beef': 'ground beef',
        'unsalted butter': 'butter',
        'salted butter': 'butter',
        'butter': 'butter',
        'olive oil': 'olive oil',
        'vegetable oil': 'vegetable oil',
        'jalapenos': 'jalapeno',
        'jalapeno': 'jalapeno',
        'onions': 'onion',
        'onion': 'onion',
        'garlic': 'garlic',
        'thyme': 'thyme',
        'shrimp': 'shrimp',
        'yeast': 'yeast',
        'flour': 'flour',
        'sugar': 'sugar',
    }
    
    text_lower = text.lower()
    for variant, base in variants.items():
        if text_lower == variant or text_lower.startswith(variant + ' '):
            return base
    
    return text.lower()


def demo_offers(query: str, *, zip_code: str | None = None, lat: float | None = None, lng: float | None = None,
                radius_miles: float = 5.0):
    """
    Return predictable demo offers for a handful of common grocery queries so the UI isn't a dead end
    without API keys. This is gated by PRICING_DEMO env in the router.

    Output schema per-offer:
      {
        'provider': 'demo', 'store': str, 'price': float|None, 'unit': str|None,
        'url': str|None, 'promo_text': str|None, 'distance_miles': float|None
      }
    """
    q = query.lower().strip()
    data = {
        'flour': [
            {'store': 'Safeway', 'price': 2.49, 'unit': '5 lb', 'promo_text': 'Club Price', 'distance_miles': 1.2},
            {'store': 'Target', 'price': 2.79, 'unit': '5 lb', 'promo_text': 'Circle Offer', 'distance_miles': 2.0},
            {'store': 'Walmart', 'price': 2.58, 'unit': '5 lb', 'promo_text': None, 'distance_miles': 3.5},
        ],
        'sugar': [
            {'store': 'Safeway', 'price': 2.19, 'unit': '4 lb', 'promo_text': 'Mix & Match', 'distance_miles': 1.2},
            {'store': 'Walmart', 'price': 2.08, 'unit': '4 lb', 'promo_text': None, 'distance_miles': 3.5},
        ],
        'yeast': [
            {'store': 'Kroger', 'price': 1.39, 'unit': '3x7g', 'promo_text': 'Weekly Ad', 'distance_miles': 4.0},
            {'store': 'Walmart', 'price': 1.24, 'unit': '3x7g', 'promo_text': None, 'distance_miles': 3.5},
        ],
        'vegetable oil': [
            {'store': 'Target', 'price': 4.79, 'unit': '48 oz', 'promo_text': None, 'distance_miles': 2.0},
            {'store': 'Safeway', 'price': 5.49, 'unit': '48 oz', 'promo_text': 'Club Price', 'distance_miles': 1.2},
        ],
        'beef': [
            {'store': 'Safeway', 'price': 4.99, 'unit': 'lb', 'promo_text': '80% lean', 'distance_miles': 1.2},
            {'store': 'Walmart', 'price': 4.68, 'unit': 'lb', 'promo_text': None, 'distance_miles': 3.5},
        ],
        'ground beef': [
            {'store': 'Safeway', 'price': 3.99, 'unit': 'lb', 'promo_text': 'Club Price 80% lean', 'distance_miles': 1.2},
            {'store': 'Smith\'s', 'price': 3.49, 'unit': 'lb', 'promo_text': 'Weekly Ad 73% lean', 'distance_miles': 4.0},
        ],
        'onion': [
            {'store': 'Raley\'s', 'price': 0.99, 'unit': 'lb', 'promo_text': 'Weekly Ad', 'distance_miles': 2.5},
            {'store': 'Safeway', 'price': 1.29, 'unit': 'lb', 'promo_text': 'Club Price', 'distance_miles': 1.2},
        ],
        'jalapeno': [
            {'store': 'Smith\'s', 'price': 0.79, 'unit': 'lb', 'promo_text': 'Weekly Ad', 'distance_miles': 4.0},
            {'store': 'Sprouts', 'price': 0.99, 'unit': 'lb', 'promo_text': 'Produce Specials', 'distance_miles': 3.8},
        ],
    }
    offers = data.get(q, [])
    return [
        {
            'provider': 'demo',
            'store': o['store'],
            'price': o['price'],
            'unit': o.get('unit'),
            'url': None,
            'promo_text': o.get('promo_text'),
            'distance_miles': o.get('distance_miles'),
        }
        for o in offers
    ]

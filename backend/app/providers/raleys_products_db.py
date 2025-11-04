"""
Raley's product database extracted from circular.
This is curated data from the October 29 - November 4, 2025 circular.
Will be replaced with dynamic PDF extraction in the future.
"""

RALEYS_PRODUCTS = {
    "Meat & Seafood": [
        {"name": "Foster Farms Split Chicken Breasts", "price": 1.97, "unit": "lb"},
        {"name": "Raley's Fresh Pork Loin Chops", "price": 2.97, "unit": "lb"},
        {"name": "Raley's Untrimmed Tri Tip Roast", "price": 5.97, "unit": "lb"},
        {"name": "Raley's Fresh Chicken Wings", "price": 3.99, "unit": "lb"},
        {"name": "Perdue Ground Chicken", "price": 5.99, "unit": "ea"},
        {"name": "Raley's Trimmed Tri Tip Roast", "price": 9.99, "unit": "lb"},
        {"name": "Pork Shoulder Roast", "price": 3.99, "unit": "lb"},
        {"name": "Raley's Natural Chuck Roast", "price": 9.99, "unit": "lb"},
        {"name": "Cold Water Lobster Tail", "price": 6.99, "unit": "ea"},
        {"name": "Fresh Tilapia Fillets", "price": 7.99, "unit": "lb"},
    ],
    "Produce": [
        {"name": "Hass Avocados", "price": 0.97, "unit": "ea"},
        {"name": "Cucumbers", "price": 0.97, "unit": "ea"},
        {"name": "Green Bell Peppers", "price": 0.97, "unit": "ea"},
        {"name": "Envy Apples", "price": 1.77, "unit": "lb"},
        {"name": "Honeycrisp Apples", "price": 1.77, "unit": "lb"},
        {"name": "Roma Tomatoes", "price": 1.99, "unit": "lb"},
        {"name": "Green Grapes", "price": 3.99, "unit": "lb"},
        {"name": "Organic Carrot Bunch", "price": 2.99, "unit": "ea"},
        {"name": "Brussels Sprouts", "price": 2.49, "unit": "lb"},
        {"name": "Pomegranates", "price": 2.99, "unit": "ea"},
        {"name": "Fuyu Persimmons", "price": 1.99, "unit": "ea"},
        {"name": "Hard Squash", "price": 1.29, "unit": "lb"},
    ],
    "Frozen & Refrigerated": [
        {"name": "Fresh Blueberries", "price": 4.97, "unit": "ea"},
        {"name": "Raley's Cage Free Eggs", "price": 4.97, "unit": "ea"},
        {"name": "Danish Creamery Butter", "price": 3.97, "unit": "ea"},
        {"name": "DiGiorno Pizza", "price": 4.97, "unit": "ea"},
        {"name": "Raley's Raw EZ Peel Jumbo Shrimp", "price": 5.97, "unit": "lb"},
        {"name": "Ben & Jerry's Gelato", "price": 4.47, "unit": "ea"},
        {"name": "Ball Park Beef Franks", "price": 4.97, "unit": "ea"},
    ],
    "Beverages": [
        {"name": "Gatorade", "price": 1.25, "unit": "ea"},
        {"name": "Peet's Coffee", "price": 8.99, "unit": "ea"},
        {"name": "Coca-Cola 2 liter", "price": 2.48, "unit": "ea"},
        {"name": "Coca-Cola 6-pack", "price": 3.97, "unit": "ea"},
    ],
    "Wine & Spirits": [
        {"name": "Apothic Wine", "price": 7.99, "unit": "ea"},
        {"name": "Ménage à Trois Wine", "price": 8.99, "unit": "ea"},
        {"name": "Brûlée Chardonnay", "price": 9.99, "unit": "ea"},
        {"name": "La Crema Monterey", "price": 17.99, "unit": "ea"},
        {"name": "Jack Daniel's Whiskey", "price": 17.99, "unit": "ea"},
        {"name": "Fireball Cinnamon Whisky", "price": 11.99, "unit": "ea"},
        {"name": "Espolón Blanco Tequila", "price": 24.99, "unit": "ea"},
    ],
    "Pantry Essentials": [
        {"name": "Yoplait Yogurt", "price": 0.39, "unit": "ea"},
        {"name": "S&W Beans", "price": 1.25, "unit": "ea"},
        {"name": "Campbell's Chunky Soup", "price": 3.00, "unit": "ea"},
        {"name": "Raley's Mac & Cheese Dinner", "price": 0.98, "unit": "ea"},
        {"name": "Raley's Cream Cheese Tub", "price": 2.99, "unit": "ea"},
        {"name": "Rosarita Refried Beans", "price": 0.37, "unit": "ea"},
    ],
}


def search_products(query: str, category: str = None) -> list:
    """
    Search for products matching a query.
    
    Args:
        query: Search term (e.g., "tri-tip", "onions")
        category: Optional category to limit search
    
    Returns:
        List of matching products with prices
    """
    query_lower = query.lower()
    matches = []
    
    # Determine which categories to search
    categories_to_search = [category] if category else list(RALEYS_PRODUCTS.keys())
    
    # Normalize query: split on both spaces and hyphens
    query_tokens = query_lower.replace("-", " ").split()
    
    for cat in categories_to_search:
        if cat not in RALEYS_PRODUCTS:
            continue
        
        for product in RALEYS_PRODUCTS[cat]:
            product_name = product["name"].lower()
            
            # Match if query is directly in product name OR all query tokens are in product name
            if query_lower in product_name or all(
                token in product_name for token in query_tokens
            ):
                matches.append({
                    **product,
                    "category": cat,
                    "store": "Raley's",
                    "source": "circular"
                })
    
    return matches


if __name__ == "__main__":
    # Test
    results = search_products("tri-tip")
    for r in results:
        print(f"{r['name']}: ${r['price']}/{r['unit']}")

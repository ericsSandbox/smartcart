"""
Reference lists for common allergens, dietary restrictions, and food preferences
Used to intelligently check recipe ingredients against household member restrictions
"""

# Common allergens (FDA's 9 major food allergens + common additions)
COMMON_ALLERGENS = {
    'milk': ['milk', 'dairy', 'cheese', 'butter', 'cream', 'yogurt', 'whey', 'casein', 'lactose'],
    'eggs': ['egg', 'eggs', 'mayonnaise', 'meringue', 'albumin'],
    'fish': ['fish', 'salmon', 'tuna', 'cod', 'halibut', 'bass', 'anchovy', 'sardine'],
    'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster', 'crayfish', 'prawn', 'clam', 'mussel', 'oyster', 'scallop'],
    'tree nuts': ['almond', 'cashew', 'walnut', 'pecan', 'pistachio', 'macadamia', 'hazelnut', 'chestnut', 'pine nut'],
    'peanuts': ['peanut', 'peanut butter', 'groundnut'],
    'wheat': ['wheat', 'flour', 'bread', 'pasta', 'couscous', 'semolina', 'durum'],
    'soybeans': ['soy', 'soybean', 'tofu', 'tempeh', 'edamame', 'miso', 'soy sauce'],
    'sesame': ['sesame', 'tahini', 'sesame seed', 'sesame oil'],
    'gluten': ['gluten', 'wheat', 'barley', 'rye', 'malt', 'beer', 'bread', 'pasta']
}

# Dietary restrictions and their prohibited foods
DIETARY_RESTRICTIONS = {
    'vegan': ['meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'fish', 'salmon', 'tuna', 'seafood', 
              'shellfish', 'shrimp', 'crab', 'dairy', 'milk', 'cheese', 'butter', 'cream', 'yogurt', 
              'egg', 'eggs', 'honey', 'gelatin'],
    'vegetarian': ['meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'fish', 'salmon', 'tuna', 
                   'seafood', 'shellfish', 'shrimp', 'crab', 'anchovy', 'gelatin'],
    'pescatarian': ['meat', 'beef', 'pork', 'chicken', 'turkey', 'lamb', 'bacon', 'sausage'],
    'keto': ['sugar', 'bread', 'pasta', 'rice', 'potato', 'corn', 'wheat', 'flour', 'oats', 'cereal'],
    'paleo': ['dairy', 'milk', 'cheese', 'yogurt', 'bread', 'pasta', 'rice', 'corn', 'beans', 
              'lentils', 'peanut', 'soy', 'sugar', 'processed'],
    'kosher': ['pork', 'bacon', 'ham', 'shellfish', 'shrimp', 'crab', 'lobster', 'clam'],
    'halal': ['pork', 'bacon', 'ham', 'alcohol', 'wine', 'beer', 'liquor'],
    'gluten-free': ['wheat', 'barley', 'rye', 'bread', 'pasta', 'flour', 'beer', 'couscous', 'semolina'],
    'dairy-free': ['milk', 'dairy', 'cheese', 'butter', 'cream', 'yogurt', 'whey', 'casein'],
    'low-carb': ['bread', 'pasta', 'rice', 'potato', 'sugar', 'flour', 'corn', 'cereal']
}

# Common food dislikes (for matching against user-entered dislikes)
COMMON_FOODS = [
    # Proteins
    'beef', 'pork', 'chicken', 'turkey', 'lamb', 'fish', 'salmon', 'tuna', 'shrimp', 'crab',
    # Vegetables
    'tomato', 'onion', 'garlic', 'broccoli', 'cauliflower', 'mushroom', 'pepper', 'celery', 
    'carrot', 'spinach', 'kale', 'brussels sprouts', 'asparagus', 'zucchini', 'eggplant',
    # Fruits
    'banana', 'apple', 'orange', 'lemon', 'lime', 'avocado', 'coconut', 'pineapple',
    # Dairy
    'cheese', 'milk', 'butter', 'cream', 'yogurt', 'blue cheese', 'goat cheese',
    # Other
    'egg', 'mayo', 'mayonnaise', 'mustard', 'vinegar', 'pickle', 'olive', 'caper',
    'cilantro', 'parsley', 'mint', 'basil', 'oregano', 'thyme', 'rosemary',
    'spicy', 'hot sauce', 'jalapeño', 'chili'
]

def check_ingredient_conflicts(ingredient_name: str, member_allergies: str = None, 
                               member_dislikes: str = None, member_dietary_pref: str = None):
    """
    Check if an ingredient conflicts with a member's restrictions
    Returns: dict with 'allergies', 'dislikes', and 'dietary' lists of conflicts
    """
    ingredient_lower = ingredient_name.lower()
    conflicts = {
        'allergies': [],
        'dislikes': [],
        'dietary': []
    }
    
    # Check allergies
    if member_allergies:
        allergies_list = [a.strip().lower() for a in member_allergies.split(',')]
        for allergen_category, allergen_foods in COMMON_ALLERGENS.items():
            if allergen_category in allergies_list or any(a in allergies_list for a in allergen_foods):
                # Check if ingredient contains this allergen
                for food in allergen_foods:
                    if food in ingredient_lower:
                        conflicts['allergies'].append(allergen_category)
                        break
    
    # Check dislikes
    if member_dislikes:
        dislikes_list = [d.strip().lower() for d in member_dislikes.split(',')]
        for dislike in dislikes_list:
            if dislike in ingredient_lower:
                conflicts['dislikes'].append(dislike)
    
    # Check dietary restrictions
    if member_dietary_pref:
        diet_prefs = [d.strip().lower() for d in member_dietary_pref.split(',')]
        for diet in diet_prefs:
            if diet in DIETARY_RESTRICTIONS:
                prohibited = DIETARY_RESTRICTIONS[diet]
                for food in prohibited:
                    if food in ingredient_lower:
                        conflicts['dietary'].append(f"{diet} (contains {food})")
                        break
    
    return conflicts

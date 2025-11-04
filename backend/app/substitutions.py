"""
Ingredient substitution suggestions based on dietary preferences and restrictions.
Based on common cooking substitutions from Allrecipes, University Extension guides, etc.
"""

# Comprehensive substitution mappings by dietary need
SUBSTITUTIONS = {
    # Vegan substitutions
    'vegan': {
        'butter': ['coconut oil (equal amount)', 'vegan butter', 'olive oil (3/4 amount)', 'applesauce (for baking, 1/2 amount)'],
        'milk': ['almond milk', 'oat milk', 'soy milk', 'coconut milk'],
        'cream': ['coconut cream', 'cashew cream', 'oat cream'],
        'heavy cream': ['coconut cream', 'cashew cream blended'],
        'sour cream': ['cashew sour cream', 'coconut yogurt', 'vegan sour cream'],
        'yogurt': ['coconut yogurt', 'almond yogurt', 'soy yogurt'],
        'cheese': ['nutritional yeast', 'vegan cheese', 'cashew cheese'],
        'parmesan': ['nutritional yeast', 'vegan parmesan'],
        'egg': ['flax egg (1 tbsp ground flax + 3 tbsp water)', 'chia egg (1 tbsp chia + 3 tbsp water)', 'applesauce (1/4 cup)', 'mashed banana (1/4 cup)'],
        'eggs': ['flax eggs', 'chia eggs', 'commercial egg replacer'],
        'mayonnaise': ['vegan mayo', 'mashed avocado', 'hummus'],
        'honey': ['maple syrup', 'agave nectar', 'date syrup'],
        'gelatin': ['agar agar', 'carrageenan'],
        'chicken broth': ['vegetable broth', 'mushroom broth'],
        'beef broth': ['vegetable broth', 'mushroom broth'],
    },
    
    # Gluten-free substitutions
    'gluten-free': {
        'flour': ['gluten-free flour blend (1:1 ratio)', 'almond flour', 'rice flour', 'coconut flour (use less, very absorbent)'],
        'all-purpose flour': ['gluten-free all-purpose flour', 'gluten-free 1:1 baking flour'],
        'wheat flour': ['gluten-free flour blend', 'rice flour + tapioca starch mix'],
        'bread': ['gluten-free bread', 'lettuce wraps', 'rice cakes'],
        'bread crumbs': ['gluten-free bread crumbs', 'crushed rice crackers', 'almond meal'],
        'breadcrumbs': ['gluten-free breadcrumbs', 'crushed cornflakes', 'ground oats (certified GF)'],
        'pasta': ['gluten-free pasta', 'rice noodles', 'zucchini noodles', 'chickpea pasta'],
        'soy sauce': ['tamari (gluten-free soy sauce)', 'coconut aminos'],
        'beer': ['gluten-free beer', 'wine', 'cider'],
        'couscous': ['quinoa', 'cauliflower rice', 'gluten-free couscous'],
        'oats': ['certified gluten-free oats'],
        'rye': ['gluten-free flour blend'],
        'barley': ['rice', 'quinoa', 'millet'],
        'semolina': ['rice flour', 'cornmeal'],
    },
    
    # Dairy-free substitutions
    'dairy-free': {
        'milk': ['almond milk', 'oat milk', 'soy milk', 'coconut milk', 'rice milk'],
        'butter': ['coconut oil', 'dairy-free margarine', 'olive oil'],
        'cream': ['coconut cream', 'cashew cream', 'oat cream'],
        'heavy cream': ['coconut cream', 'cashew cream'],
        'sour cream': ['coconut yogurt', 'cashew sour cream', 'dairy-free sour cream'],
        'yogurt': ['coconut yogurt', 'almond yogurt', 'soy yogurt'],
        'cheese': ['nutritional yeast', 'dairy-free cheese', 'cashew cheese'],
        'cream cheese': ['dairy-free cream cheese', 'cashew cheese spread'],
        'ice cream': ['coconut milk ice cream', 'oat milk ice cream', 'sorbet'],
        'whipped cream': ['coconut whipped cream', 'aquafaba whipped'],
    },
    
    # Low-carb/Keto substitutions
    'keto': {
        'sugar': ['erythritol', 'stevia', 'monk fruit sweetener', 'allulose'],
        'flour': ['almond flour', 'coconut flour (use 1/4 amount)', 'flaxseed meal'],
        'bread': ['cloud bread', 'lettuce wraps', 'keto bread'],
        'pasta': ['zucchini noodles', 'shirataki noodles', 'spaghetti squash'],
        'rice': ['cauliflower rice', 'broccoli rice'],
        'potato': ['cauliflower', 'radishes (roasted)', 'turnips'],
        'potatoes': ['cauliflower', 'radishes', 'turnips'],
        'oats': ['hemp hearts', 'chia seeds', 'flaxseed meal'],
        'corn': ['cauliflower', 'zucchini'],
        'breadcrumbs': ['pork rinds (crushed)', 'almond flour', 'parmesan'],
    },
    
    # Paleo substitutions
    'paleo': {
        'sugar': ['honey', 'maple syrup', 'coconut sugar', 'date paste'],
        'flour': ['almond flour', 'coconut flour', 'cassava flour', 'arrowroot powder'],
        'butter': ['ghee', 'coconut oil', 'avocado oil'],
        'milk': ['almond milk', 'coconut milk'],
        'cheese': ['nutritional yeast', 'cashew cheese'],
        'yogurt': ['coconut yogurt'],
        'soy sauce': ['coconut aminos'],
        'peanut butter': ['almond butter', 'cashew butter', 'sunflower seed butter'],
        'bread': ['grain-free bread', 'lettuce wraps', 'sweet potato'],
        'pasta': ['zucchini noodles', 'sweet potato noodles', 'spaghetti squash'],
        'rice': ['cauliflower rice', 'sweet potato'],
        'beans': ['sweet potato', 'butternut squash', 'cauliflower'],
    },
    
    # Common allergen substitutions
    'nut-free': {
        'almond': ['sunflower seeds', 'pumpkin seeds (pepitas)', 'oats'],
        'almonds': ['sunflower seeds', 'pumpkin seeds'],
        'almond flour': ['sunflower seed flour', 'oat flour', 'coconut flour'],
        'almond milk': ['oat milk', 'rice milk', 'hemp milk', 'coconut milk'],
        'peanut butter': ['sunflower seed butter', 'tahini', 'soy nut butter'],
        'cashew': ['sunflower seeds', 'hemp seeds'],
        'cashews': ['sunflower seeds', 'hemp seeds', 'white beans (for cream)'],
        'walnut': ['pumpkin seeds', 'sunflower seeds'],
        'walnuts': ['pumpkin seeds', 'sunflower seeds'],
        'pecan': ['sunflower seeds', 'pumpkin seeds'],
        'pecans': ['sunflower seeds', 'pumpkin seeds'],
    },
    
    'egg-free': {
        'egg': ['flax egg (1 tbsp ground flax + 3 tbsp water)', 'chia egg', 'applesauce (1/4 cup)', 'mashed banana (1/4 cup)', 'commercial egg replacer'],
        'eggs': ['flax eggs', 'chia eggs', 'aquafaba (3 tbsp per egg)', 'silken tofu (1/4 cup blended)'],
    },
}

# General healthy substitutions (always suggest these)
HEALTHY_SWAPS = {
    'white sugar': ['coconut sugar', 'honey', 'maple syrup (reduce liquid)', 'date paste'],
    'vegetable oil': ['olive oil', 'avocado oil', 'coconut oil'],
    'white flour': ['whole wheat flour', 'spelt flour', 'oat flour'],
    'sour cream': ['greek yogurt', 'cottage cheese (blended)'],
    'mayonnaise': ['greek yogurt', 'mashed avocado'],
    'white rice': ['brown rice', 'quinoa', 'cauliflower rice'],
    'white bread': ['whole grain bread', 'sprouted grain bread'],
    'cream': ['evaporated milk', 'greek yogurt'],
    'salt': ['herbs and spices', 'lemon juice', 'nutritional yeast'],
}


def get_substitutions(ingredient_name: str, dietary_preferences: list[str] = None) -> dict:
    """
    Get substitution suggestions for an ingredient based on dietary preferences.
    
    Args:
        ingredient_name: The ingredient to find substitutions for
        dietary_preferences: List of dietary preferences (vegan, gluten-free, etc.)
    
    Returns:
        Dictionary with 'dietary' and 'healthy' substitution lists
    """
    ingredient_lower = ingredient_name.lower().strip()
    results = {
        'dietary': [],  # Substitutions based on dietary restrictions
        'healthy': []   # General healthy alternatives
    }
    
    # Check dietary substitutions
    if dietary_preferences:
        for diet in dietary_preferences:
            diet_key = diet.lower().strip()
            if diet_key in SUBSTITUTIONS:
                diet_subs = SUBSTITUTIONS[diet_key]
                for key, subs in diet_subs.items():
                    if key in ingredient_lower or ingredient_lower in key:
                        for sub in subs:
                            if sub not in results['dietary']:
                                results['dietary'].append({
                                    'substitute': sub,
                                    'reason': f'{diet} alternative'
                                })
    
    # Check healthy swaps
    for key, subs in HEALTHY_SWAPS.items():
        if key in ingredient_lower or ingredient_lower in key:
            for sub in subs:
                if sub not in [s['substitute'] for s in results['healthy']]:
                    results['healthy'].append({
                        'substitute': sub,
                        'reason': 'Healthier option'
                    })
    
    return results


def suggest_substitutions_for_recipe(ingredients: list[str], household_dietary_prefs: list[str]) -> dict:
    """
    Analyze a full recipe and suggest substitutions for ingredients.
    
    Args:
        ingredients: List of ingredient strings from recipe
        household_dietary_prefs: Combined dietary preferences from all household members
    
    Returns:
        Dictionary mapping ingredient names to their substitution suggestions
    """
    suggestions = []
    
    for ingredient in ingredients:
        subs = get_substitutions(ingredient, household_dietary_prefs)
        if subs['dietary'] or subs['healthy']:
            # subs already contains objects: {'substitute': str, 'reason': str}
            suggestions.append({
                'ingredient': ingredient,
                'dietary_subs': subs['dietary'],
                'healthy_subs': subs['healthy']
            })
    
    return suggestions

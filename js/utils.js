// ============================================
// UTILITY FUNCTIONS
// ============================================

// Calculate Levenshtein distance between two strings
export function levenshteinDistance(str1, str2) {
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = [];

    for (let i = 0; i <= len1; i++) {
        matrix[i] = [i];
    }

    for (let j = 0; j <= len2; j++) {
        matrix[0][j] = j;
    }

    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            if (str1[i - 1] === str2[j - 1]) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // substitution
                    matrix[i][j - 1] + 1,     // insertion
                    matrix[i - 1][j] + 1      // deletion
                );
            }
        }
    }

    return matrix[len1][len2];
}

// Find similar item names (returns null if exact match or no close match)
export function findSimilarItem(inputName, existingItems) {
    const input = inputName.toLowerCase().trim();
    
    // Check for exact match first
    const exactMatch = existingItems.find(item => 
        item.name.toLowerCase() === input
    );
    if (exactMatch) {
        return { type: 'exact', item: exactMatch };
    }

    // Find close matches (within 2 character edits)
    let bestMatch = null;
    let bestDistance = Infinity;

    existingItems.forEach(item => {
        const itemName = item.name.toLowerCase();
        const distance = levenshteinDistance(input, itemName);
        
        // Consider it a potential typo if:
        // 1. Distance is 1-2 characters for short words (<=8 chars)
        // 2. Distance is 1-3 characters for longer words
        const threshold = input.length <= 8 ? 2 : 3;
        
        if (distance > 0 && distance <= threshold && distance < bestDistance) {
            bestDistance = distance;
            bestMatch = item;
        }
    });

    if (bestMatch) {
        return { type: 'similar', item: bestMatch, distance: bestDistance };
    }

    return null;
}

// Category patterns for auto-categorization
export const CATEGORY_PATTERNS = {
    'Proteins': [
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'bacon', 'sausage', 'steak',
        'lamb', 'shrimp', 'crab', 'lobster', 'tofu', 'tempeh', 'seitan', 'egg', 'ground beef',
        'ground pork', 'ground turkey', 'ground chicken', 'ham', 'prosciutto', 'salami', 'pepperoni'
    ],
    'Fruits': [
        'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'raspberry', 'blackberry',
        'mango', 'pineapple', 'watermelon', 'cantaloupe', 'honeydew', 'kiwi', 'peach', 'pear',
        'plum', 'cherry', 'lemon', 'lime', 'grapefruit', 'avocado', 'cranberr', 'lingonberr'
    ],
    'Vegetables': [
        'lettuce', 'tomato', 'cucumber', 'carrot', 'broccoli', 'cauliflower', 'spinach', 'kale',
        'cabbage', 'onion', 'garlic', 'pepper', 'potato', 'sweet potato', 'zucchini', 'eggplant',
        'celery', 'asparagus', 'green bean', 'pea', 'corn', 'mushroom', 'radish', 'beet', 'squash'
    ],
    'Spices': [
        'cinnamon', 'paprika', 'cumin', 'oregano', 'basil', 'thyme', 'rosemary', 'sage', 'parsley',
        'cilantro', 'dill', 'mint', 'chili', 'cayenne', 'curry', 'turmeric', 'ginger', 'nutmeg',
        'clove', 'cardamom', 'coriander', 'fennel', 'bay leaf', 'pepper', 'salt', 'vanilla',
        'allspice', 'anise', 'celery seed', 'mustard seed', 'poppy seed', 'sesame seed',
        'ground ginger', 'ground cumin', 'ground coriander', 'ground cayenne', 'ground allspice',
        'ground cinnamon', 'ground nutmeg', 'ground turmeric', 'ground cardamom'
    ],
    'Condiments': [
        'ketchup', 'mustard', 'mayo', 'mayonnaise', 'relish', 'pickle', 'sauce', 'dressing',
        'vinaigrette', 'salsa', 'hot sauce', 'soy sauce', 'worcestershire', 'bbq', 'teriyaki',
        'honey', 'syrup', 'maple', 'agave', 'molasses', 'pesto', 'tapenade', 'chutney', 'aioli',
        'tahini', 'harissa', 'sriracha', 'gochujang', 'miso', 'hoisin', 'fish sauce'
    ],
    'Oils & Vinegars': [
        'olive oil', 'vegetable oil', 'canola oil', 'coconut oil', 'sesame oil', 'avocado oil',
        'grapeseed oil', 'sunflower oil', 'peanut oil', 'vinegar', 'balsamic', 'apple cider vinegar',
        'red wine vinegar', 'white wine vinegar', 'rice vinegar', 'cooking spray'
    ],
    'Grains & Pasta': [
        'rice', 'pasta', 'noodle', 'spaghetti', 'penne', 'macaroni', 'quinoa', 'couscous', 'bulgur',
        'barley', 'oat', 'wheat', 'farro', 'polenta', 'grits', 'orzo', 'ramen', 'udon', 'soba',
        'linguine', 'fettuccine', 'rigatoni', 'farfalle', 'tortellini', 'ravioli'
    ],
    'Baking': [
        'flour', 'sugar', 'brown sugar', 'powdered sugar', 'baking powder', 'baking soda', 'yeast',
        'cornstarch', 'cocoa', 'chocolate chip', 'vanilla extract', 'almond extract', 'coconut extract',
        'baking chocolate', 'sprinkles', 'food coloring', 'gelatin'
    ],
    'Frozen': [
        'frozen', 'ice cream', 'popsicle', 'frozen pizza', 'frozen veget', 'frozen fruit',
        'frozen meal', 'frozen dinner', 'frozen entree', 'frozen dessert', 'sorbet', 'gelato'
    ],
    'Bakery': [
        'bread', 'bun', 'roll', 'bagel', 'croissant', 'muffin', 'donut', 'danish', 'scone',
        'baguette', 'ciabatta', 'focaccia', 'pita', 'naan', 'tortilla', 'flatbread', 'english muffin'
    ],
    'Dairy & Cheese': [
        'milk', 'cheese', 'yogurt', 'butter', 'cream', 'sour cream', 'cottage cheese', 'ricotta',
        'mozzarella', 'cheddar', 'parmesan', 'brie', 'feta', 'gouda', 'swiss', 'provolone',
        'blue cheese', 'goat cheese', 'cream cheese', 'half and half', 'whipping cream',
        'buttermilk', 'condensed milk', 'evaporated milk', 'almond milk', 'soy milk', 'oat milk'
    ],
    'Pantry': [
        'crackers', 'granola', 'cereal', 'soup', 'beans', 'canned', 'coconut water',
        'vegetarian', 'baked beans', 'jam', 'jellied', 'grenadine', 'gravy'
    ],
    'Household': [
        'ziplock', 'plastic', 'wrap', 'foil', 'aluminum', 'parchment', 'bag',
        'paper', 'sandwich', 'gallon'
    ]
};

// Auto-categorize an item based on its name
export function autoCategorizePantryItem(itemName) {
    if (!itemName) return 'Pantry';
    const nameLower = itemName.toLowerCase();
    
    // Check for specific compound patterns first (e.g., "ground cumin" vs generic "ground")
    // This ensures "ground cumin" matches Spices before anything else
    const compoundPatterns = [
        'ground ginger', 'ground cumin', 'ground coriander', 'ground cayenne', 'ground allspice',
        'ground cinnamon', 'ground nutmeg', 'ground turmeric', 'ground cardamom',
        'ground beef', 'ground pork', 'ground turkey', 'ground chicken'
    ];
    
    for (const pattern of compoundPatterns) {
        if (nameLower.includes(pattern)) {
            // Find which category this compound belongs to
            for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
                if (patterns.includes(pattern)) {
                    return category;
                }
            }
        }
    }
    
    // Then check regular patterns
    for (const [category, patterns] of Object.entries(CATEGORY_PATTERNS)) {
        for (const pattern of patterns) {
            if (nameLower.includes(pattern)) {
                return category;
            }
        }
    }
    return 'Pantry';
}

// Check if an item is expired
export function isExpired(expiresAt) {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
}

// Get human-readable expiration status
export function getExpiresIn(expiresAt) {
    if (!expiresAt) return '';
    const date = new Date(expiresAt);
    const today = new Date();
    const diff = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
    
    if (diff < 0) return 'Expired';
    if (diff === 0) return 'Expires today';
    if (diff === 1) return 'Expires tomorrow';
    if (diff < 7) return `Expires in ${diff} days`;
    return date.toLocaleDateString();
}

// Category display configuration
export const CATEGORY_EMOJIS = {
    'Proteins': '🍗',
    'Fruits': '🍎',
    'Vegetables': '🥬',
    'Spices': '🧂',
    'Condiments': '🍯',
    'Oils & Vinegars': '🫒',
    'Grains & Pasta': '🌾',
    'Baking': '🎂',
    'Frozen': '❄️',
    'Bakery': '🥖',
    'Dairy & Cheese': '🧀',
    'Pantry': '📦',
    'Household': '🏠'
};

export const CATEGORY_ORDER = [
    'Proteins', 'Fruits', 'Vegetables', 'Spices', 'Condiments', 'Oils & Vinegars',
    'Grains & Pasta', 'Baking', 'Frozen', 'Bakery', 'Dairy & Cheese', 'Pantry', 'Household'
];

// Tile colors for pantry items
export const TILE_COLORS = [
    '#e0f2fe', // light blue
    '#f0fdf4', // light green
    '#fef3c7', // light yellow
    '#ffe4e6', // light pink
    '#f3e8ff', // light purple
    '#e5e7eb'  // light gray
];

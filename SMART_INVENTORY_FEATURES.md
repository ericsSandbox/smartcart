# SmartCart Smart Inventory Features

## Overview
SmartCart now includes three intelligent inventory management features that work together to prevent duplicates, organize your pantry, and streamline shopping list creation from recipes.

---

## 1. Smart Duplicate Detection During Inventory
**Purpose:** When inventorying your pantry, avoid creating duplicate entries if you find multiple items with the same name.

### How It Works
When you add an item to the pantry, SmartCart:
1. **Checks if the item already exists** (case-insensitive exact match)
2. **If found:** Increments the quantity of the existing item instead of creating a new entry
3. **If not found:** Creates a new pantry item
4. **Shows user feedback** via confirmation message

### Example Scenario
**You're inventorying and find ground cumin twice:**

```
First entry: Add "ground cumin" (qty: 1)
  ✅ Result: "Created new entry: ground cumin"
  Pantry now shows: ground cumin (1 unit)

Second entry: Add "ground cumin" (qty: 1)  
  ✅ Result: "Smart Duplicate Detection!
             Added 1 unit(s) to existing 'ground cumin'
             Old total: 1 unit
             New total: 2 units"
  Pantry now shows: ground cumin (2 units)
```

### Technical Details
- **Matching:** Case-insensitive, exact name match (after trimming whitespace)
- **Quantity Update:** Old quantity + new quantity = new total
- **Data Preservation:** All other properties (unit, expiration, staple flag, category) remain unchanged
- **Applied to:** Manual entry, barcode scan, and manual/scanned lookup

### Where to Find It
- Manual entry: "Add Item to Pantry" form → Add Item button
- Barcode scan: After scanning a product
- Manual lookup: When manually entering product info after barcode lookup

---

## 2. Smart Pantry Categorization
**Purpose:** Automatically organize your pantry items into logical groups for easy browsing and management.

### How It Works
SmartCart automatically assigns each item to a category based on its name:

#### Categories (12 total)
1. **🍗 Proteins** - chicken, beef, pork, turkey, bacon, fish, shrimp, steak, etc.
2. **🥬 Vegetables** - cucumber, onion, carrot, celery, lettuce, broccoli, tomato, etc.
3. **🧂 Spices** - turmeric, ginger, cumin, paprika, cinnamon, oregano, etc.
4. **🍯 Condiments** - ketchup, mayo, mustard, sriracha, hot sauce, ranch dressing, etc.
5. **🫒 Oils & Vinegars** - olive oil, vegetable oil, balsamic vinegar, wine vinegar, etc.
6. **🌾 Grains & Pasta** - rice, pasta, bread, flour, lentils, beans, crackers, etc.
7. **🎂 Baking** - sugar, flour, yeast, vanilla extract, baking soda, honey, etc.
8. **❄️ Frozen** - frozen peas, pizza dough, hot pockets, lasagna, ice cream, etc.
9. **🥖 Bakery** - bagels, bread, egg roll wrappers, pita, tortillas, etc.
10. **🧀 Dairy & Cheese** - milk, cheese, butter, yogurt, cream, eggs, etc.
11. **📦 Pantry** - canned soup, crackers, jam, coconut water, etc.
12. **🏠 Household** - ziplock bags, plastic wrap, aluminum foil, parchment paper, etc.

### View Modes
SmartCart provides two ways to view your pantry:

**📂 View: Categories (Default)**
- Items grouped by category with emoji headers
- Shows item count per category
- Collapsible sections for organization
- Perfect for browsing by food type

**📋 View: Items**
- Traditional list of all items
- Search still works across all items
- Better for quick quantity adjustments

### Toggle Between Views
Press the **📂 View: Categories** button (or **📋 View: Items** after switching) in the Pantry tab.
Your preference is saved automatically.

### Example View
```
🍗 Proteins (4)
  • Chicken breast (4 units)
  • Pork loin (2 units)
  • Sliced turkey breast (3 units)
  • Freezer bacon (2 units)

🥬 Vegetables (3)
  • Cucumber (7 units)
  • Onions (8 units)
  • Carrots (6 units)

🧂 Spices (39)
  • Turmeric (1 unit)
  • Ground ginger (1 unit)
  • Curry powder (1 unit)
  [... and 36 more]
```

### Auto-Categorization Algorithm
- Pattern-based keyword matching (100+ patterns)
- Case-insensitive matching
- Searches full item name, not just first word
- Examples:
  - "ground cumin" → Spices (matches "cumin")
  - "sliced turkey breast" → Proteins (matches "turkey" and "breast")
  - "frozen peas" → Frozen (matches "frozen")
  - "pizza cheese" → Dairy & Cheese (matches "cheese")

### Important Notes
- **New items:** Automatically categorized based on their name
- **Existing items:** Auto-categorized on first app load
- **Manual override:** Currently categorized automatically; custom categories coming soon
- **Uncategorized items:** Default to "Pantry" category if no pattern matches

---

## 3. Smart Ingredient Import with Pantry Cross-Reference
**Purpose:** Import recipe ingredients into shopping lists while automatically skipping items you already have in the pantry.

### How It Works
When you paste ingredients from a recipe:

1. **Parse ingredients** (handles: "10 oz rice", "1 lb ground beef", "soy sauce")
2. **Extract base ingredient** (removes descriptors like "ground", "frozen", "sliced")
3. **Check pantry** for exact base match
4. **Add to shopping list** only if NOT already in pantry
5. **Show summary** of what was added vs. skipped

### Example Scenario
**You paste ingredients for a recipe:**
```
2 cups rice
1 lb ground beef
2 onions
2 tbsp soy sauce
frozen peas
ground ginger
```

**Your pantry has:**
- Rice (10 cups)
- Onions (8 units)
- Ground ginger (1 unit)

**Result:**
```
✅ Added 3 items to shopping list!

⏭️ Skipped 3 items (already in pantry):
  • Rice (pantry has: 10 cup)
  • Onions (pantry has: 8 unit)
  • Ground ginger (pantry has: 1 unit)

Shopping list now has:
  • Ground beef (1 lb)
  • Soy sauce (2 tbsp)
  • Frozen peas (1 unit)
```

### Descriptor Removal
SmartCart removes common descriptors when matching, so:

| Original Ingredient | Base Match | Pantry Check |
|---|---|---|
| 1 lb ground beef | beef | "beef" in pantry? |
| 2 tbsp fresh ginger | ginger | "ginger" in pantry? |
| frozen peas | peas | "peas" in pantry? |
| 1 cup shredded cheese | cheese | "cheese" in pantry? |
| diced tomatoes | tomatoes | "tomatoes" in pantry? |

**Descriptors Recognized:**
- Preparation: ground, sliced, diced, minced, shredded, grated, chopped, crushed
- Condition: fresh, dried, frozen, canned, cooked, roasted, raw, toasted
- Quality: organic, whole, half, seedless, boneless, skinless, unsalted, salted
- Texture: powdered, paste, sauce, liquid
- Flavor: spicy, hot, sweet, vanilla, chocolate, caramel

### Where to Find It
1. Open the app's Add Item modal (+ button)
2. Click "🍳 Find Recipes" tab
3. Search for a recipe (e.g., "pasta", "chicken stir fry")
4. Or manually enter ingredients in the ingredient paste area
5. Select your shopping list
6. Paste ingredients (one per line or comma-separated)
7. Click "Import Ingredients"

### Ingredient Format Examples
SmartCart can parse these formats:
```
10 oz rice noodles
1 lb ground beef
2 cups sugar
1/2 cup milk
0.5 tbsp salt
soy sauce
garlic
fresh basil
frozen peas
```

### Important Notes
- **Flexible parsing:** Handles various formats with quantities, units, and descriptors
- **Smart matching:** Case-insensitive, extracts base ingredient name
- **Pantry first:** Assumes you want to use what you have before buying
- **User control:** Shows what was skipped so you can manually add if needed
- **No duplicates in shopping list:** Items already in that shopping list are not re-added

---

## Feature Interactions

### Complete Workflow Example
**Scenario:** You want to make a stir-fry tonight

1. **Search for recipe** in app → find "vegetable stir fry"
2. **Copy ingredients** from recipe website:
   ```
   2 cups basmati rice
   1 lb chicken breast
   3 cups mixed vegetables
   4 tbsp soy sauce
   2 tbsp sesame oil
   ```

3. **Paste into SmartCart** → ingredient import with pantry cross-ref:
   ```
   ✅ Added 2 items (soy sauce, sesame oil)
   ⏭️ Skipped 3 items already in pantry:
     • Basmati rice
     • Chicken breast  
     • Mixed vegetables
   ```

4. **Check shopping list** → Only needs soy sauce and sesame oil

5. **When you return from shopping:**
   - Add items manually (triggers duplicate detection) → automatically updates quantity if already have them

6. **View pantry by category** to quickly find everything:
   - 🥬 Vegetables → find "mixed vegetables"
   - 🍗 Proteins → find "chicken breast"
   - 🌾 Grains → find "rice"
   - 🫒 Oils → find "sesame oil"
   - 🍯 Condiments → find "soy sauce"

7. **Cook and enjoy!**

---

## Smart Inventory Benefits

### Time Savings
- No more duplicate entries during inventory
- Skip pantry items automatically when making shopping lists
- Organized by category = faster browsing

### Accuracy
- Base ingredient matching reduces duplicate shopping
- "Frozen peas" automatically skipped if you have "peas"
- "Ground beef" recognized as "beef" for smarter matching

### User Experience
- Clear feedback on what was added/skipped
- Search works across all views
- View preferences saved automatically
- Multiple viewing/filtering options

---

## Future Enhancements

### Planned Features
- [ ] Custom category creation and assignment
- [ ] Category-based filtering in views
- [ ] Smart recipe suggestions based on pantry contents
- [ ] Item-level category editing
- [ ] Shopping list completion tracking by category
- [ ] Allergen filtering across recipes and pantry
- [ ] Multi-household category syncing

---

## FAQ

**Q: What if an item matches multiple categories?**
A: SmartCart uses the first matching category. For example, "ground cumin" matches "Spices" before any other category.

**Q: Can I change an item's category?**
A: Currently categories are auto-assigned. Manual override coming soon!

**Q: What if my ingredient doesn't parse correctly?**
A: Try formatting as: "quantity unit ingredient" (e.g., "2 cups sugar") or just the ingredient name (e.g., "basil").

**Q: Does ingredient import work with my existing shopping lists?**
A: Yes! Just select which shopping list to add ingredients to.

**Q: What if I accidentally create a duplicate?**
A: The duplicate detection on the next add will merge them. Or you can manually edit quantities.

**Q: Are categories case-sensitive?**
A: No! "CHICKEN breast", "chicken BREAST", and "Chicken Breast" all categorize as Proteins.

**Q: What happens if I disable the app and re-enable it?**
A: All your pantry items keep their assigned categories, stored in localStorage alongside the item data.

---

## Technical Implementation

### Files Modified
- `index.html` - All smart features implemented in vanilla JavaScript

### Functions Added/Updated
- `findDuplicateItem(itemName)` - Case-insensitive duplicate detection
- `addManualItem()` - Updated with duplicate detection
- `addManualScanned()` - Updated with duplicate detection  
- `addScannedItem()` - Updated with duplicate detection
- `autoCategorizePantryItem(itemName)` - Pattern-based categorization
- `extractBaseIngredient(ingredientName)` - Descriptor removal for import
- `importIngredients()` - Updated with pantry cross-reference
- `renderPantryByCategory()` - New categorized pantry view
- `migratePantryToCategories()` - Auto-categorize items on load
- `togglePantryView()` - Switch between views with persistence

### Data Structure
```javascript
// Pantry item with category
{
  id: 1762710428280,
  name: "ground cumin",
  quantity: 2,
  unit: "unit",
  category: "Spices",  // New field
  expires_at: null,
  isStaple: false
}
```

### Performance
- Categorization: O(n) on load, O(1) per item thereafter (cached)
- Duplicate detection: O(n) linear search (fast for <500 items)
- Ingredient import: O(m × n) where m=ingredients, n=pantry items (acceptable)

---

## Version History

### v2.1 (Current)
- ✅ Smart duplicate detection for inventory
- ✅ Automatic pantry categorization (12 categories)
- ✅ Categorized pantry view with emoji headers
- ✅ View toggle with persistence
- ✅ Smart ingredient import with pantry cross-reference
- ✅ Base ingredient extraction (40+ descriptors)

### v2.0
- Data backup/restore system
- Shopping list workflow (Shop, Done, Renew buttons)
- Staples feature with auto-Staples list
- CSV export

### v1.0
- Initial release with basic pantry/shopping management

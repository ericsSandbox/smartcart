# 📝 Import Ingredients Feature - Quick Paste Shopping Lists

New feature: Paste raw ingredient lists from recipes directly into shopping lists!

## 🎯 How to Use

### 1. Open a Shopping List
- Go to **Shopping** tab
- Click **+** button
- Select an existing list OR create a new one

### 2. Click "Import" Tab
- You'll see a textarea with placeholder text
- Shows examples of formats it accepts

### 3. Paste Your Ingredients
Copy ingredients from any recipe and paste them in. Works with:

**With quantities:**
```
10 oz rice noodles
1 lb ground beef
2 cups sugar
0.5 cup milk
3 tbsp butter
1 can tomato sauce
```

**Without quantities:**
```
soy sauce
salt
pepper
garlic
green onions
```

**Mixed format:**
```
10 oz rice noodles
1 lb ground beef
soy sauce
sugar
salt
pepper
maple syrup
garlic
green onions
everything bagel seasoning
```

### 4. Click "Import All"
All ingredients are automatically added to your shopping list!

## ✨ Smart Parsing

The parser intelligently extracts:

| Input | Result |
|-------|--------|
| `10 oz rice noodles` | 10 oz rice noodles |
| `1 lb ground beef` | 1 lb ground beef |
| `2 cups sugar` | 2 cup sugar |
| `3 tbsp butter` | 3 tbsp butter |
| `0.5 cup milk` | 0.5 cup milk |
| `soy sauce` | 1 unit soy sauce |
| `salt` | 1 unit salt |
| `1 can tomato sauce` | 1 can tomato sauce |

## 📋 Supported Units

Automatically recognized units:
- `oz` - ounces
- `lb` - pounds
- `g` - grams
- `kg` - kilograms
- `cup` / `cups` - cups
- `tbsp` - tablespoons
- `tsp` - teaspoons
- `ml` - milliliters
- `l` - liters
- `can`, `jar`, `box`, `bag` - containers
- `piece`, `pieces` - individual items

## 🔧 Example Workflow

**You find this recipe:**
```
Thai Ground Beef Noodle Bowl

Ingredients:
10 oz rice noodles
1 lb ground beef
2 tbsp soy sauce
1 tbsp sugar
salt and pepper
1 tbsp maple syrup
2 cloves garlic
2 green onions
1 tbsp everything bagel seasoning
```

**You want to shop for it:**

1. Go to Shopping tab → Click +
2. Create list: "Thai Noodle Bowl"
3. Click Import tab
4. Paste all ingredients (one per line):
   ```
   10 oz rice noodles
   1 lb ground beef
   2 tbsp soy sauce
   1 tbsp sugar
   salt and pepper
   1 tbsp maple syrup
   2 cloves garlic
   2 green onions
   1 tbsp everything bagel seasoning
   ```
5. Click "Import All"
6. **BAM!** All 9 items instantly in your shopping list with quantities!

## ✅ What You Get

After import, you'll see:
- ✅ Each item as a separate line item
- ✅ Quantities parsed automatically (e.g., "10 oz")
- ✅ Units recognized (e.g., "tbsp", "oz")
- ✅ Proper formatting for easy shopping
- ✅ Checkboxes to mark off as you shop

## ❓ Formatting Tips

**Best format:**
```
10 oz rice noodles
1 lb ground beef
2 tbsp soy sauce
```

**Also works:**
```
rice noodles (10 oz)
ground beef - 1 lb
soy sauce 2 tbsp
```

**Simple items (no quantity):**
```
salt
pepper
garlic
```

## 🐛 Troubleshooting

**Not parsing correctly?**
- Make sure one ingredient per line
- Include quantity before the unit (e.g., "10 oz", not "oz 10")
- Quantity must be a number (1, 2, 0.5, 3.5, etc)

**Item added with wrong quantity?**
- It will show in the list - you can edit it manually
- Click the item to adjust quantity/unit

**Some items not added?**
- The import shows how many were successful
- Items that couldn't parse appear in the error message
- Try reformatting and importing again

## 💡 Pro Tips

- **Multiple recipes**: Import ingredients from multiple recipes into one list
- **Adjust quantities**: After importing, edit individual items to adjust
- **Double-check units**: Review imports to make sure units are correct
- **Save failed items**: Failed items are shown so you can add them manually

---

**Example: Paste this and try it!**

```
10 oz rice noodles
1 lb ground beef
soy sauce
sugar
salt
pepper
maple syrup
garlic
green onions
everything bagel seasoning
```

Result: 10 items instantly added to your shopping list! ✨

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from ..substitutions import suggest_substitutions_for_recipe

from recipe_scrapers import scrape_html
import re

router = APIRouter(prefix="/recipes", tags=["recipes"])


class RecipeImportRequest(BaseModel):
    household_id: int
    url: str
    create_list: bool = False
    servings_multiplier: float = 1.0  # Multiplier for recipe quantities
    exclude_ingredients: list[str] = []  # Ingredients to exclude from shopping list

class IngredientConflict(BaseModel):
    ingredient: str
    member_name: str
    conflict_type: str  # 'allergy', 'dislike', or 'dietary'
    details: str


class SubstitutionSuggestion(BaseModel):
    ingredient: str
    dietary_subs: list[dict] = []  # [{'substitute': str, 'reason': str}]
    healthy_subs: list[dict] = []  # [{'substitute': str, 'reason': str}]


class RecipeImportResponse(BaseModel):
    title: str
    servings: int | None
    ingredients: list[str]
    missing: list[str]
    conflicts: list[IngredientConflict] = []
    substitutions: list[SubstitutionSuggestion] = []
    created_list_id: int | None = None


class AddRecipeToListRequest(BaseModel):
    recipe_id: int
    servings_multiplier: float = 1.0
    exclude_ingredients: list[str] = []


class AddRecipeToListResponse(BaseModel):
    conflicts: list[IngredientConflict] = []
    substitutions: list[SubstitutionSuggestion] = []
    created_list_id: int | None = None


def normalize_name(s: str) -> str:
    s = s.lower()
    # remove quantities like 1, 1/2, 2-3, 10oz, (optional)
    s = re.sub(r"\d+[\d/\-.]*", " ", s)
    s = re.sub(r"\(.*?\)", " ", s)
    # remove punctuation
    s = re.sub(r"[^a-zA-Z\s]", " ", s)
    # remove common stopwords
    stop = {"of", "and", "or", "to", "a", "an", "the"}
    tokens = [t for t in s.split() if t and t not in stop]
    return " ".join(tokens).strip()


@router.post("/import", response_model=RecipeImportResponse)
def import_recipe(payload: RecipeImportRequest, db: Session = Depends(get_db)):
    household = crud.get_household(db, payload.household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")

    # Normalize URL - ensure it has a scheme
    url = payload.url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    def fallback_parse_recipe_html(html_text: str, page_url: str):
        # Very lightweight fallback: try JSON-LD then <title>
        title_fb = None
        servings_fb = None
        ingredients_fb: list[str] = []
        try:
            # Try to find JSON-LD with recipeIngredient
            # Greedy block then find all strings inside recipeIngredient array
            m = re.search(r'"recipeIngredient"\s*:\s*\[(.*?)\]', html_text, re.IGNORECASE | re.DOTALL)
            if m:
                block = m.group(1)
                ingredients_fb = [s.strip() for s in re.findall(r'"(.*?)"', block) if s.strip()]
            # recipeYield
            my = re.search(r'"recipeYield"\s*:\s*"(.*?)"', html_text, re.IGNORECASE)
            if my:
                ys = my.group(1)
                mn = re.search(r"(\d+)", ys)
                if mn:
                    servings_fb = int(mn.group(1))
            # <title>
            mt = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
            if mt:
                title_fb = re.sub(r"\s+", " ", mt.group(1)).strip()
        except Exception:
            pass
        if not title_fb:
            from urllib.parse import urlparse
            p = urlparse(page_url)
            title_fb = p.netloc
        return title_fb or "Recipe", servings_fb, ingredients_fb

    try:
        # Add User-Agent to avoid 403 Forbidden from sites that block scrapers
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Fetch the page with custom headers
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # First try recipe-scrapers
        try:
            scraper = scrape_html(html=response.text, org_url=url)
            title = scraper.title().strip() if scraper.title() else "Recipe"
            try:
                servings = scraper.yields()
                if isinstance(servings, str):
                    m = re.search(r"(\d+)", servings)
                    servings = int(m.group(1)) if m else None
            except Exception:
                servings = None
            ingredients = [i.strip() for i in (scraper.ingredients() or []) if i and i.strip()]
        except Exception:
            # Fallback parse for unsupported sites
            title, servings, ingredients = fallback_parse_recipe_html(response.text, url)
    except Exception as e:
        import traceback
        error_detail = f"Failed to scrape recipe. Error: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to console
        # Final fallback if even fetch failed
        raise HTTPException(status_code=400, detail=f"Failed to scrape recipe. The site may not be supported. Error: {str(e)[:200]}")

    # build pantry name set
    pantry = crud.get_pantry_items(db, payload.household_id)
    pantry_names = {normalize_name(p.name) for p in pantry}

    # Get household members for conflict checking
    members = crud.get_members_for_household(db, payload.household_id)
    
    # Check ingredients for conflicts
    from ..food_lists import check_ingredient_conflicts
    conflicts: list[IngredientConflict] = []
    
    missing: list[str] = []
    for ing in ingredients:
        n = normalize_name(ing)
        # if any pantry name is a substring of ingredient or exact match consider it present
        present = any(n == pn or pn in n or n in pn for pn in pantry_names if pn)
        if not present:
            missing.append(ing)
        
        # Check this ingredient against all members' restrictions
        for member in members:
            member_conflicts = check_ingredient_conflicts(
                ing,
                member_allergies=member.allergies,
                member_dislikes=member.dislikes,
                member_dietary_pref=member.dietary_pref
            )
            
            # Add allergy conflicts (critical)
            for allergen in member_conflicts['allergies']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='allergy',
                    details=f"Contains {allergen}"
                ))
            
            # Add dietary conflicts
            for diet_issue in member_conflicts['dietary']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='dietary',
                    details=diet_issue
                ))
            
            # Add dislikes
            for dislike in member_conflicts['dislikes']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='dislike',
                    details=f"Dislikes {dislike}"
                ))
    
    # Get substitution suggestions based on household dietary preferences
    all_dietary_prefs = [m.dietary_pref for m in members if m.dietary_pref]
    substitutions = suggest_substitutions_for_recipe(ingredients, all_dietary_prefs)

    created_list_id: int | None = None
    if payload.create_list and missing:
        # create a shopping list and add missing ingredients as names
        lst = crud.create_shopping_list(db, schemas.ShoppingListCreate(name=f"Recipe: {title}", household_id=payload.household_id))
        created_list_id = lst.id
        
        # Filter out excluded ingredients
        excluded_set = set(payload.exclude_ingredients)
        
        for ing in missing:
            # Skip if this ingredient is in the exclusion list
            if ing in excluded_set:
                continue
                
            try:
                # Note: servings_multiplier will be applied when quantities are parsed from ingredient names
                # The parsing happens in crud.add_list_item via parse_quantity_from_name
                crud.add_list_item(db, lst.id, schemas.ShoppingListItemCreate(name=ing, quantity=payload.servings_multiplier, unit="unit", notes=None))
            except Exception:
                pass

    return RecipeImportResponse(title=title, servings=servings, ingredients=ingredients, missing=missing, conflicts=conflicts, substitutions=substitutions, created_list_id=created_list_id)


@router.get("/saved/{household_id}", response_model=list[schemas.SavedRecipe])
def get_saved_recipes(household_id: int, db: Session = Depends(get_db)):
    return crud.get_saved_recipes(db, household_id)


@router.post("/saved", response_model=schemas.SavedRecipe)
def save_recipe(recipe: schemas.SavedRecipeCreate, db: Session = Depends(get_db)):
    return crud.create_saved_recipe(db, recipe)


@router.delete("/saved/{recipe_id}")
def delete_saved_recipe(recipe_id: int, household_id: int, db: Session = Depends(get_db)):
    success = crud.delete_saved_recipe(db, recipe_id, household_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"success": True}


@router.post("/saved/add-to-list", response_model=AddRecipeToListResponse)
def add_saved_recipe_to_list(payload: AddRecipeToListRequest, db: Session = Depends(get_db)):
    # Get the saved recipe
    recipe = db.query(crud.models.SavedRecipe).filter(crud.models.SavedRecipe.id == payload.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    household = crud.get_household(db, recipe.household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    # Get household members for conflict checking
    members = crud.get_members_for_household(db, recipe.household_id)
    
    # Get pantry items to check what's missing
    pantry = crud.get_pantry_items(db, recipe.household_id)
    pantry_names = {normalize_name(p.name) for p in pantry}
    
    # Check ingredients for conflicts and determine what's missing
    from ..food_lists import check_ingredient_conflicts
    conflicts: list[IngredientConflict] = []
    missing: list[str] = []
    
    ingredients = [ing.name for ing in recipe.ingredients]
    
    for ing in ingredients:
        n = normalize_name(ing)
        present = any(n == pn or pn in n or n in pn for pn in pantry_names if pn)
        if not present:
            missing.append(ing)
        
        # Check conflicts
        for member in members:
            member_conflicts = check_ingredient_conflicts(
                ing,
                member_allergies=member.allergies,
                member_dislikes=member.dislikes,
                member_dietary_pref=member.dietary_pref
            )
            
            for allergen in member_conflicts['allergies']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='allergy',
                    details=f"Contains {allergen}"
                ))
            
            for diet_issue in member_conflicts['dietary']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='dietary',
                    details=diet_issue
                ))
            
            for dislike in member_conflicts['dislikes']:
                conflicts.append(IngredientConflict(
                    ingredient=ing,
                    member_name=member.name,
                    conflict_type='dislike',
                    details=f"Dislikes {dislike}"
                ))
    
    # Get substitution suggestions
    all_dietary_prefs = [m.dietary_pref for m in members if m.dietary_pref]
    substitutions = suggest_substitutions_for_recipe(ingredients, all_dietary_prefs)
    
    # Create shopping list with missing ingredients
    created_list_id: int | None = None
    if missing:
        lst = crud.create_shopping_list(db, schemas.ShoppingListCreate(
            name=f"Recipe: {recipe.title}",
            household_id=recipe.household_id
        ))
        created_list_id = lst.id
        
        excluded_set = set(payload.exclude_ingredients)
        
        for ing in missing:
            if ing in excluded_set:
                continue
            
            try:
                crud.add_list_item(db, lst.id, schemas.ShoppingListItemCreate(
                    name=ing,
                    quantity=payload.servings_multiplier,
                    unit="unit",
                    notes=None
                ))
            except Exception:
                pass
    
    return AddRecipeToListResponse(
        conflicts=conflicts,
        substitutions=substitutions,
        created_list_id=created_list_id
    )

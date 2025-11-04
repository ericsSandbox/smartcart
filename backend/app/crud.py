from sqlalchemy.orm import Session
from . import models, schemas
import re


def parse_quantity_from_name(name: str):
    """
    Extract quantity and unit from ingredient name like "2 tbsp. all-purpose flour"
    Returns: (cleaned_name, extracted_quantity, extracted_unit)
    """
    # Pattern to match quantities at the start: "2 tbsp", "1/2 cup", "1.5 oz", etc.
    pattern = r'^(\d+(?:[./]\d+)?(?:\s*\d+/\d+)?)\s*(tbsp\.?|tsp\.?|cup|oz\.?|lb\.?|g|kg|ml|l|qt\.?|pt\.?|gal\.?|c\.?)?\s+'
    match = re.match(pattern, name, re.IGNORECASE)
    
    if match:
        qty_str = match.group(1)
        unit_str = match.group(2) or 'unit'
        
        # Parse quantity (handle fractions like "1/2" or "1 1/2")
        try:
            if '/' in qty_str:
                parts = qty_str.split()
                if len(parts) == 2:  # "1 1/2"
                    whole = float(parts[0])
                    frac = parts[1].split('/')
                    qty = whole + (float(frac[0]) / float(frac[1]))
                else:  # "1/2"
                    frac = qty_str.split('/')
                    qty = float(frac[0]) / float(frac[1])
            else:
                qty = float(qty_str)
        except:
            qty = 1.0
        
        # Normalize unit (remove periods, lowercase)
        unit = unit_str.lower().rstrip('.')
        
        # Remove the matched quantity/unit from name
        cleaned_name = name[match.end():].strip()
        
        return cleaned_name, qty, unit
    
    return name, None, None


def create_household(db: Session, household: schemas.HouseholdCreate):
    db_household = models.Household(name=household.name, budget=getattr(household, 'budget', None))
    db.add(db_household)
    db.commit()
    db.refresh(db_household)

    # create members if provided
    if getattr(household, 'members', None):
        for m in household.members:
            db_member = models.Member(
                household_id=db_household.id,
                name=m.name,
                role=getattr(m, 'role', 'adult'),
                age=getattr(m, 'age', None),
                allergies=getattr(m, 'allergies', None),
                dislikes=getattr(m, 'dislikes', None),
                dietary_pref=getattr(m, 'dietary_pref', None)
            )
            db.add(db_member)
        db.commit()
        db.refresh(db_household)

    return db_household


def get_household(db: Session, household_id: int):
    return db.query(models.Household).filter(models.Household.id == household_id).first()


def list_households(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Household).offset(skip).limit(limit).all()


# Members
def get_members_for_household(db: Session, household_id: int):
    return db.query(models.Member).filter(models.Member.household_id == household_id).all()


def add_member(db: Session, household_id: int, member: schemas.MemberCreate):
    db_member = models.Member(
        household_id=household_id,
        name=member.name,
        role=getattr(member, 'role', 'adult'),
        age=getattr(member, 'age', None),
        allergies=getattr(member, 'allergies', None),
        dislikes=getattr(member, 'dislikes', None),
        likes=getattr(member, 'likes', None),
        favorite_recipes=getattr(member, 'favorite_recipes', None),
        dietary_pref=getattr(member, 'dietary_pref', None),
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_member(db: Session, member_id: int, updates: schemas.MemberUpdate):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        return None
    data = updates.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(member, k, v)
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> bool:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


# Shopping lists
def create_shopping_list(db: Session, shopping_list: schemas.ShoppingListCreate):
    db_list = models.ShoppingList(name=shopping_list.name, household_id=shopping_list.household_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


def get_shopping_list(db: Session, list_id: int):
    return db.query(models.ShoppingList).filter(models.ShoppingList.id == list_id).first()


def get_lists_for_household(db: Session, household_id: int):
    return db.query(models.ShoppingList).filter(models.ShoppingList.household_id == household_id).all()


def add_list_item(db: Session, list_id: int, item: schemas.ShoppingListItemCreate):
    # Parse quantity/unit from name if present
    cleaned_name, parsed_qty, parsed_unit = parse_quantity_from_name(item.name)
    
    # Use parsed values if found, otherwise use provided values
    name = cleaned_name
    quantity = parsed_qty if parsed_qty is not None else item.quantity
    unit = parsed_unit if parsed_unit is not None else item.unit
    
    # If item.quantity is provided and parsed_qty exists, treat item.quantity as a multiplier
    if parsed_qty is not None and item.quantity != 1.0:
        quantity = parsed_qty * item.quantity
    
    db_item = models.ShoppingListItem(list_id=list_id, name=name, quantity=quantity, unit=unit, notes=item.notes)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items_for_list(db: Session, list_id: int):
    return db.query(models.ShoppingListItem).filter(models.ShoppingListItem.list_id == list_id).all()


def update_shopping_list(db: Session, list_id: int, updates: schemas.ShoppingListBase):
    lst = get_shopping_list(db, list_id)
    if not lst:
        return None
    data = updates.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(lst, k, v)
    db.commit()
    db.refresh(lst)
    return lst


def delete_shopping_list(db: Session, list_id: int) -> bool:
    lst = get_shopping_list(db, list_id)
    if not lst:
        return False
    
    # If this is a "Staples" list, remove the staple flag from all pantry items
    if lst.name and lst.name.lower() == "staples":
        pantry_items = db.query(models.PantryItem).filter(
            models.PantryItem.household_id == lst.household_id,
            models.PantryItem.staple == True
        ).all()
        for item in pantry_items:
            item.staple = False
    
    db.delete(lst)
    db.commit()
    return True


def update_list_item(db: Session, item_id: int, updates: schemas.ShoppingListItemBase):
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        return None
    data = updates.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


def delete_list_item(db: Session, item_id: int) -> bool:
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def move_list_item_to_pantry(db: Session, item_id: int) -> models.PantryItem | None:
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        return None
    lst = get_shopping_list(db, item.list_id)
    if not lst:
        return None
    household_id = lst.household_id
    
    # Clean up ingredient name: remove prep methods and extra details
    import re
    name = item.name
    # Remove anything in parentheses
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove common prep words at end (diced, chopped, minced, sliced, etc.)
    prep_words = r'\b(diced|chopped|minced|sliced|cubed|grated|shredded|crushed|peeled|trimmed|halved|quartered)\b'
    name = re.sub(prep_words, '', name, flags=re.IGNORECASE)
    # Clean up extra whitespace and commas
    name = re.sub(r'\s*,\s*', ' ', name)
    name = ' '.join(name.split()).strip()
    
    # Normalize liquid quantities to 1L
    liquid_units = {'tbsp', 'tsp', 'cup', 'ml', 'oz', 'qt', 'pt', 'gal'}
    unit = (item.unit or 'unit').lower()
    quantity = item.quantity or 1.0
    
    if unit in liquid_units:
        # Assume purchased in 1L bottles/containers
        quantity = 1.0
        unit = 'l'
    
    # Check if item with similar name already exists in pantry
    existing = db.query(models.PantryItem).filter(
        models.PantryItem.household_id == household_id,
        models.PantryItem.name.ilike(f'%{name}%')
    ).first()
    
    if existing and existing.unit == unit:
        # Consolidate with existing item
        existing.quantity = (existing.quantity or 0) + quantity
        db.commit()
        db.refresh(existing)
        # Mark shopping list item as shopped instead of deleting
        item.shopped = True
        db.commit()
        return existing
    
    # Create new pantry item
    pantry_item = models.PantryItem(
        household_id=household_id,
        name=name,
        quantity=quantity,
        unit=unit,
        expires_at=None,
        staple=0,
    )
    db.add(pantry_item)
    # Mark shopping list item as shopped instead of deleting
    item.shopped = True
    db.commit()
    db.refresh(pantry_item)
    return pantry_item


def restore_list_item(db: Session, item_id: int) -> models.ShoppingListItem | None:
    item = db.query(models.ShoppingListItem).filter(models.ShoppingListItem.id == item_id).first()
    if not item:
        return None
    item.shopped = False
    db.commit()
    db.refresh(item)
    return item


def get_or_create_staples_list(db: Session, household_id: int) -> models.ShoppingList:
    lst = (
        db.query(models.ShoppingList)
        .filter(models.ShoppingList.household_id == household_id, models.ShoppingList.name == "Staples")
        .first()
    )
    if lst:
        return lst
    # create Staples list
    payload = schemas.ShoppingListCreate(name="Staples", household_id=household_id)
    return create_shopping_list(db, payload)


def add_or_update_item_by_name(db: Session, list_id: int, name: str, quantity: float = 1.0, unit: str = "unit", notes: str | None = None):
    # Parse quantity/unit from name if present
    cleaned_name, parsed_qty, parsed_unit = parse_quantity_from_name(name)
    
    # Use parsed values if found, otherwise use provided values
    if parsed_qty is not None:
        quantity = parsed_qty
    if parsed_unit is not None:
        unit = parsed_unit
    name = cleaned_name
    
    existing = (
        db.query(models.ShoppingListItem)
        .filter(models.ShoppingListItem.list_id == list_id, models.ShoppingListItem.name == name)
        .first()
    )
    if existing:
        # Prefer max to avoid shrinking inadvertently; adjust as needed
        existing.quantity = max(existing.quantity or 0, quantity)
        if unit:
            existing.unit = unit
        if notes is not None:
            existing.notes = notes
        db.commit()
        db.refresh(existing)
        return existing
    # create new
    create_payload = schemas.ShoppingListItemCreate(name=name, quantity=quantity, unit=unit, notes=notes)
    return add_list_item(db, list_id, create_payload)


# Pantry
def get_pantry_items(db: Session, household_id: int):
    return db.query(models.PantryItem).filter(models.PantryItem.household_id == household_id).all()


def add_pantry_item(db: Session, household_id: int, item: schemas.PantryItemCreate):
    # Parse quantity/unit from name if present
    cleaned_name, parsed_qty, parsed_unit = parse_quantity_from_name(item.name)
    
    # Use parsed values if found, otherwise use provided values
    name = cleaned_name
    quantity = parsed_qty if parsed_qty is not None else item.quantity
    unit = parsed_unit if parsed_unit is not None else item.unit
    
    db_item = models.PantryItem(
        household_id=household_id,
        name=name,
        quantity=quantity,
        unit=unit,
        expires_at=getattr(item, 'expires_at', None),
        staple=1 if getattr(item, 'staple', False) else 0,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    # Staples automation: if staple and quantity <= 0, ensure item is on Staples list
    try:
        is_staple = bool(getattr(item, 'staple', False))
        qty = float(quantity or 0)
        if is_staple and qty <= 0:
            staples = get_or_create_staples_list(db, household_id)
            add_or_update_item_by_name(db, staples.id, name=name, quantity=1, unit=unit)
    except Exception:
        # non-fatal in dev
        pass
    return db_item


def update_pantry_item(db: Session, household_id: int, item_id: int, updates: schemas.PantryItemUpdate):
    item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id, models.PantryItem.household_id == household_id).first()
    if not item:
        return None
    data = updates.dict(exclude_unset=True)
    # normalize staple to bool if present
    if 'staple' in data and data['staple'] is not None:
        data['staple'] = bool(data['staple'])
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    
    # Staples automation: if item is a staple and quantity drops to 0 or below, auto-add to Staples list
    try:
        is_staple = bool(item.staple)
        qty = float(item.quantity or 0)
        if is_staple and qty <= 0:
            staples = get_or_create_staples_list(db, household_id)
            add_or_update_item_by_name(db, staples.id, name=item.name, quantity=1, unit=item.unit)
    except Exception:
        pass
    
    return item


def delete_pantry_item(db: Session, household_id: int, item_id: int) -> bool:
    item = db.query(models.PantryItem).filter(models.PantryItem.id == item_id, models.PantryItem.household_id == household_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


# Saved Recipes CRUD
def create_saved_recipe(db: Session, recipe: schemas.SavedRecipeCreate):
    db_recipe = models.SavedRecipe(
        household_id=recipe.household_id,
        title=recipe.title,
        url=recipe.url,
        servings=recipe.servings
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Add ingredients
    for ing_name in recipe.ingredients:
        db_ingredient = models.SavedRecipeIngredient(recipe_id=db_recipe.id, name=ing_name)
        db.add(db_ingredient)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


def get_saved_recipes(db: Session, household_id: int):
    return db.query(models.SavedRecipe).filter(models.SavedRecipe.household_id == household_id).all()


def get_saved_recipe(db: Session, recipe_id: int, household_id: int):
    return db.query(models.SavedRecipe).filter(
        models.SavedRecipe.id == recipe_id,
        models.SavedRecipe.household_id == household_id
    ).first()


def delete_saved_recipe(db: Session, recipe_id: int, household_id: int) -> bool:
    recipe = get_saved_recipe(db, recipe_id, household_id)
    if not recipe:
        return False
    db.delete(recipe)
    db.commit()
    return True


# Household Settings CRUD
def get_household_settings(db: Session, household_id: int) -> models.HouseholdSettings | None:
    return db.query(models.HouseholdSettings).filter(models.HouseholdSettings.household_id == household_id).first()


def upsert_household_settings(db: Session, payload: schemas.HouseholdSettingsCreate) -> models.HouseholdSettings:
    settings = get_household_settings(db, payload.household_id)
    if settings is None:
        settings = models.HouseholdSettings(household_id=payload.household_id)
        db.add(settings)
    settings.pricing_enabled = payload.pricing_enabled
    settings.zip_code = payload.zip_code
    settings.latitude = payload.latitude
    settings.longitude = payload.longitude
    settings.radius_miles = payload.radius_miles or 5.0
    db.commit()
    db.refresh(settings)
    return settings

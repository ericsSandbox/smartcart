"""
API routes for household-based resource management
Maps /households/{household_id}/* endpoints to individual routers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/households", tags=["households"])

# ============================================
# PANTRY ENDPOINTS
# ============================================

@router.get("/{household_id}/pantry", response_model=list[schemas.PantryItem])
def get_pantry_items(household_id: int, db: Session = Depends(get_db)):
    """Get all pantry items for a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.get_pantry_items(db, household_id)


@router.post("/{household_id}/pantry", response_model=schemas.PantryItem)
def create_pantry_item(household_id: int, item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    """Create a pantry item in a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.add_pantry_item(db, household_id, item)


@router.patch("/{household_id}/pantry/{item_id}", response_model=schemas.PantryItem)
def update_pantry_item(household_id: int, item_id: int, updates: schemas.PantryItemUpdate, db: Session = Depends(get_db)):
    """Update a pantry item"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    item = crud.update_pantry_item(db, household_id, item_id, updates)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{household_id}/pantry/{item_id}")
def delete_pantry_item(household_id: int, item_id: int, db: Session = Depends(get_db)):
    """Delete a pantry item"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    ok = crud.delete_pantry_item(db, household_id, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}


# ============================================
# SHOPPING LIST ENDPOINTS
# ============================================

@router.get("/{household_id}/lists", response_model=list[schemas.ShoppingList])
def get_shopping_lists(household_id: int, db: Session = Depends(get_db)):
    """Get all shopping lists for a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.get_lists_for_household(db, household_id)


@router.post("/{household_id}/lists", response_model=schemas.ShoppingList)
def create_shopping_list(household_id: int, list_data: schemas.ShoppingListCreate, db: Session = Depends(get_db)):
    """Create a shopping list in a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    # Add household_id to the list data
    list_data.household_id = household_id
    return crud.create_shopping_list(db, list_data)


@router.delete("/{household_id}/lists/{list_id}")
def delete_shopping_list(household_id: int, list_id: int, db: Session = Depends(get_db)):
    """Delete a shopping list"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    ok = crud.delete_shopping_list(db, list_id)
    if not ok:
        raise HTTPException(status_code=404, detail="List not found")
    return {"ok": True}


# ============================================
# MEMBERS ENDPOINTS
# ============================================

@router.get("/{household_id}/members", response_model=list[schemas.Member])
def get_household_members(household_id: int, db: Session = Depends(get_db)):
    """Get all members in a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.get_members_for_household(db, household_id)


@router.post("/{household_id}/members", response_model=schemas.Member)
def create_household_member(household_id: int, member: schemas.MemberCreate, db: Session = Depends(get_db)):
    """Create a member in a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.add_member(db, household_id, member)


@router.delete("/{household_id}/members/{member_id}")
def delete_household_member(household_id: int, member_id: int, db: Session = Depends(get_db)):
    """Delete a member from a household"""
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    ok = crud.delete_member(db, member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"ok": True}

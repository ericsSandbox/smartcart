from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/lists", tags=["lists"])

@router.post("/", response_model=schemas.ShoppingList)
def create_list(payload: schemas.ShoppingListCreate, db: Session = Depends(get_db)):
    # Basic check that household exists
    from ..crud import get_household
    household = get_household(db, payload.household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.create_shopping_list(db, payload)

@router.get("/household/{household_id}", response_model=list[schemas.ShoppingList])
def get_household_lists(household_id: int, db: Session = Depends(get_db)):
    return crud.get_lists_for_household(db, household_id)

@router.post("/{list_id}/items", response_model=schemas.ShoppingListItem)
def add_item_to_list(list_id: int, item: schemas.ShoppingListItemCreate, db: Session = Depends(get_db)):
    lst = crud.get_shopping_list(db, list_id)
    if lst is None:
        raise HTTPException(status_code=404, detail="List not found")
    return crud.add_list_item(db, list_id, item)

@router.get("/{list_id}/items", response_model=list[schemas.ShoppingListItem])
def get_items(list_id: int, db: Session = Depends(get_db)):
    return crud.get_items_for_list(db, list_id)


@router.patch("/{list_id}", response_model=schemas.ShoppingList)
def update_list(list_id: int, payload: schemas.ShoppingListBase, db: Session = Depends(get_db)):
    lst = crud.update_shopping_list(db, list_id, payload)
    if lst is None:
        raise HTTPException(status_code=404, detail="List not found")
    return lst


@router.delete("/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_shopping_list(db, list_id)
    if not ok:
        raise HTTPException(status_code=404, detail="List not found")
    return {"ok": True}


@router.patch("/items/{item_id}", response_model=schemas.ShoppingListItem)
def update_item(item_id: int, payload: schemas.ShoppingListItemBase, db: Session = Depends(get_db)):
    item = crud.update_list_item(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_list_item(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}


@router.post("/items/{item_id}/shopped")
def mark_item_shopped(item_id: int, db: Session = Depends(get_db)):
    pantry_item = crud.move_list_item_to_pantry(db, item_id)
    if pantry_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"moved_to_pantry": pantry_item.id}


@router.post("/items/{item_id}/restore")
def restore_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.restore_list_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.get("/households/{household_id}/pantry", response_model=list[schemas.PantryItem])
def get_pantry(household_id: int, db: Session = Depends(get_db)):
    # ensure household exists
    household = crud.get_household(db, household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.get_pantry_items(db, household_id)


@router.post("/households/{household_id}/pantry", response_model=schemas.PantryItem)
def add_pantry(household_id: int, item: schemas.PantryItemCreate, db: Session = Depends(get_db)):
    household = crud.get_household(db, household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.add_pantry_item(db, household_id, item)


@router.patch("/households/{household_id}/pantry/{item_id}", response_model=schemas.PantryItem)
def update_pantry(household_id: int, item_id: int, updates: schemas.PantryItemUpdate, db: Session = Depends(get_db)):
    household = crud.get_household(db, household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    item = crud.update_pantry_item(db, household_id, item_id, updates)
    if item is None:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return item


@router.delete("/households/{household_id}/pantry/{item_id}")
def delete_pantry(household_id: int, item_id: int, db: Session = Depends(get_db)):
    household = crud.get_household(db, household_id)
    if household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    ok = crud.delete_pantry_item(db, household_id, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Pantry item not found")
    return {"ok": True}

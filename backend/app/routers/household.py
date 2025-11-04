from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/households", tags=["households"]) 

@router.post("/", response_model=schemas.Household)
def create_household(household: schemas.HouseholdCreate, db: Session = Depends(get_db)):
    return crud.create_household(db, household)

@router.get("/{household_id}", response_model=schemas.Household)
def read_household(household_id: int, db: Session = Depends(get_db)):
    db_household = crud.get_household(db, household_id)
    if not db_household:
        raise HTTPException(status_code=404, detail="Household not found")
    return db_household

@router.get("/", response_model=list[schemas.Household])
def list_households(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_households(db, skip=skip, limit=limit)

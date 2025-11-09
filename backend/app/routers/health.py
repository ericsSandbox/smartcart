from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/init")
async def init_household(db: Session = Depends(get_db)):
    """Get or create default household for the frontend to use"""
    # Try to get household with ID 1
    household = crud.get_household(db, 1)
    
    if household is None:
        # Create default household
        household_data = schemas.HouseholdCreate(name="My Household")
        household = crud.create_household(db, household_data)
    
    return {
        "household_id": household.id,
        "household_name": household.name,
        "status": "ready"
    }

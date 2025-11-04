from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/members", tags=["members"]) 

@router.get("/households/{household_id}", response_model=list[schemas.Member])
def list_members(household_id: int, db: Session = Depends(get_db)):
    return crud.get_members_for_household(db, household_id)

@router.post("/households/{household_id}", response_model=schemas.Member)
def add_member(household_id: int, member: schemas.MemberCreate, db: Session = Depends(get_db)):
    # ensure household exists
    household = crud.get_household(db, household_id)
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return crud.add_member(db, household_id, member)

@router.patch("/{member_id}", response_model=schemas.Member)
def update_member(member_id: int, updates: schemas.MemberUpdate, db: Session = Depends(get_db)):
    updated = crud.update_member(db, member_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated

@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_member(db, member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "deleted"}

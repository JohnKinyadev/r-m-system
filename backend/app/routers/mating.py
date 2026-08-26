from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.db.session import get_db
from app.db.models.animals import Animal, AnimalGender
from app.db.models.mating_events import MatingEvent
from app.db.models.births import Birth
from app.db.models.livestock_types import LivestockType
from app.db.models.users import User
from app.schemas.mating import MatingEventCreate, MatingEventRead, BirthCreate, BirthRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/mating", tags=["mating"])


@router.get("", response_model=List[MatingEventRead])
def list_mating_events(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MatingEvent).order_by(MatingEvent.mating_date.desc()).all()


@router.post("", response_model=MatingEventRead, status_code=status.HTTP_201_CREATED)
def create_mating_event(
    payload: MatingEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    female = db.query(Animal).filter(Animal.id == payload.female_id).first()
    male = db.query(Animal).filter(Animal.id == payload.male_id).first()
    if not female or not male:
        raise HTTPException(status_code=404, detail="One or both animals not found")
    if female.gender != AnimalGender.female:
        raise HTTPException(status_code=400, detail="female_id must reference a female animal")
    if male.gender != AnimalGender.male:
        raise HTTPException(status_code=400, detail="male_id must reference a male animal")

    gestation = None
    if female.livestock_type and female.livestock_type.gestation_period_days:
        gestation = female.livestock_type.gestation_period_days

    expected_birth = (
        payload.mating_date + timedelta(days=gestation) if gestation else None
    )

    event = MatingEvent(
        **payload.model_dump(),
        expected_birth_date=expected_birth,
        logged_by=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/births", response_model=List[BirthRead])
def list_births(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Birth).order_by(Birth.birth_date.desc()).all()


@router.post("/births", response_model=BirthRead, status_code=status.HTTP_201_CREATED)
def log_birth(
    payload: BirthCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Animal).filter(Animal.id == payload.animal_id).first():
        raise HTTPException(status_code=404, detail="Mother animal not found")
    birth = Birth(**payload.model_dump(), logged_by=current_user.id)
    db.add(birth)
    db.commit()
    db.refresh(birth)
    return birth

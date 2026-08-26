from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.livestock_types import LivestockType
from app.db.models.vaccine_schedules import VaccineSchedule
from app.db.models.users import User
from app.schemas.livestock_types import LivestockTypeCreate, LivestockTypeRead, LivestockTypeUpdate
from app.core.dependencies import get_current_user, require_owner

router = APIRouter(prefix="/api/livestock-types", tags=["livestock-types"])


@router.get("", response_model=List[LivestockTypeRead])
def list_livestock_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(LivestockType).all()


@router.get("/{lt_id}", response_model=LivestockTypeRead)
def get_livestock_type(lt_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    lt = db.query(LivestockType).filter(LivestockType.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Livestock type not found")
    return lt


@router.post("", response_model=LivestockTypeRead, status_code=status.HTTP_201_CREATED)
def create_livestock_type(
    payload: LivestockTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    lt = LivestockType(
        name=payload.name,
        breed=payload.breed,
        gestation_period_days=payload.gestation_period_days,
        average_lifespan_years=payload.average_lifespan_years,
        created_by=current_user.id,
    )
    db.add(lt)
    db.flush()
    for vs in payload.vaccine_schedules:
        db.add(VaccineSchedule(livestock_type_id=lt.id, **vs.model_dump()))
    db.commit()
    db.refresh(lt)
    return lt


@router.patch("/{lt_id}", response_model=LivestockTypeRead)
def update_livestock_type(
    lt_id: int,
    payload: LivestockTypeUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_owner),
):
    lt = db.query(LivestockType).filter(LivestockType.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Livestock type not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(lt, field, value)
    db.commit()
    db.refresh(lt)
    return lt


@router.delete("/{lt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_livestock_type(lt_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    lt = db.query(LivestockType).filter(LivestockType.id == lt_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Livestock type not found")
    db.delete(lt)
    db.commit()

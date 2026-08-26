from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_current_user, require_module, require_owner
from app.db.models.properties import Property, PropertyStatus
from app.db.models.units import UnitStatus
from app.db.session import get_db
from app.schemas.properties import PropertyCreate, PropertyRead, PropertyUpdate

router = APIRouter(prefix="/api/properties", tags=["properties"])


def _enrich(prop: Property) -> dict:
    units = prop.units or []
    return {
        **{c.name: getattr(prop, c.name) for c in Property.__table__.columns},
        "total_units": len(units),
        "occupied_units": len([u for u in units if u.status in [UnitStatus.occupied, UnitStatus.notice_given]]),
        "vacant_units": len([u for u in units if u.status == UnitStatus.vacant]),
    }


@router.get("", response_model=List[PropertyRead])
def list_properties(
    status_filter: Optional[PropertyStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _=Depends(require_module("properties")),
):
    q = db.query(Property).order_by(Property.name)
    if status_filter:
        q = q.filter(Property.status == status_filter)
    return [_enrich(p) for p in q.all()]


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(property_id: int, db: Session = Depends(get_db), _=Depends(require_module("properties"))):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return _enrich(prop)


@router.post("", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_property(payload: PropertyCreate, db: Session = Depends(get_db), _=Depends(require_owner)):
    if db.query(Property).filter(Property.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Property code already exists")
    prop = Property(**payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return _enrich(prop)


@router.patch("/{property_id}", response_model=PropertyRead)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_owner),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return _enrich(prop)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import require_module, require_owner
from app.db.models.properties import Property
from app.db.models.units import Unit, UnitRentHistory, UnitStatus
from app.db.session import get_db
from app.routers.rental_utils import current_tenancy_for_unit, tenancy_balance
from app.schemas.units import UnitCreate, UnitRead, UnitUpdate

router = APIRouter(prefix="/api/units", tags=["units"])


def _enrich(unit: Unit, db: Session) -> dict:
    tenancy = current_tenancy_for_unit(db, unit.id)
    return {
        **{c.name: getattr(unit, c.name) for c in Unit.__table__.columns},
        "property_name": unit.property.name if unit.property else None,
        "current_tenant_name": tenancy.tenant.full_name if tenancy and tenancy.tenant else None,
        "current_tenancy_id": tenancy.id if tenancy else None,
        "balance": tenancy_balance(db, tenancy.id) if tenancy else 0,
    }


@router.get("", response_model=List[UnitRead])
def list_units(
    property_id: Optional[int] = None,
    status_filter: Optional[UnitStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _=Depends(require_module("units")),
):
    q = db.query(Unit).join(Property).order_by(Property.name, Unit.unit_number)
    if property_id:
        q = q.filter(Unit.property_id == property_id)
    if status_filter:
        q = q.filter(Unit.status == status_filter)
    return [_enrich(u, db) for u in q.all()]


@router.get("/{unit_id}", response_model=UnitRead)
def get_unit(unit_id: int, db: Session = Depends(get_db), _=Depends(require_module("units"))):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return _enrich(unit, db)


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
def create_unit(payload: UnitCreate, db: Session = Depends(get_db), _=Depends(require_owner)):
    if not db.query(Property).filter(Property.id == payload.property_id).first():
        raise HTTPException(status_code=404, detail="Property not found")
    exists = db.query(Unit).filter(
        Unit.property_id == payload.property_id,
        Unit.unit_number == payload.unit_number,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Unit already exists for this property")
    unit = Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    db.add(UnitRentHistory(unit_id=unit.id, rent_amount=unit.monthly_rent, effective_from=unit.created_at))
    db.commit()
    db.refresh(unit)
    return _enrich(unit, db)


@router.patch("/{unit_id}", response_model=UnitRead)
def update_unit(
    unit_id: int,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_owner),
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    data = payload.model_dump(exclude_none=True)
    old_rent = unit.monthly_rent
    for field, value in data.items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    if "monthly_rent" in data and unit.monthly_rent != old_rent:
        db.add(UnitRentHistory(
            unit_id=unit.id,
            rent_amount=unit.monthly_rent,
            effective_from=unit.created_at,
            changed_by_id=current_user.id,
            notes="Rent changed from unit profile",
        ))
        db.commit()
    return _enrich(unit, db)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(unit_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()

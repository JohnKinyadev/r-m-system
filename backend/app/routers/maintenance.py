from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import require_module
from app.db.models.maintenance_requests import MaintenanceRequest, MaintenanceStatus
from app.db.models.properties import Property
from app.db.models.tenants import Tenant
from app.db.models.units import Unit
from app.db.models.users import User
from app.db.session import get_db
from app.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestRead,
    MaintenanceRequestUpdate,
)

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


def _enrich(item: MaintenanceRequest) -> dict:
    return {
        **{c.name: getattr(item, c.name) for c in MaintenanceRequest.__table__.columns},
        "property_name": item.property.name if item.property else None,
        "unit_number": item.unit.unit_number if item.unit else None,
        "tenant_name": item.tenant.full_name if item.tenant else None,
        "assigned_to_name": item.assigned_to.full_name if item.assigned_to else None,
    }


@router.get("", response_model=List[MaintenanceRequestRead])
def list_maintenance_requests(
    status_filter: Optional[MaintenanceStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _=Depends(require_module("maintenance")),
):
    q = db.query(MaintenanceRequest).order_by(MaintenanceRequest.reported_date.desc(), MaintenanceRequest.id.desc())
    if status_filter:
        q = q.filter(MaintenanceRequest.status == status_filter)
    return [_enrich(item) for item in q.all()]


@router.post("", response_model=MaintenanceRequestRead, status_code=status.HTTP_201_CREATED)
def create_maintenance_request(
    payload: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    _=Depends(require_module("maintenance")),
):
    if not db.query(Property).filter(Property.id == payload.property_id).first():
        raise HTTPException(status_code=404, detail="Property not found")
    if payload.unit_id and not db.query(Unit).filter(Unit.id == payload.unit_id).first():
        raise HTTPException(status_code=404, detail="Unit not found")
    if payload.tenant_id and not db.query(Tenant).filter(Tenant.id == payload.tenant_id).first():
        raise HTTPException(status_code=404, detail="Tenant not found")
    if payload.assigned_to_id and not db.query(User).filter(User.id == payload.assigned_to_id).first():
        raise HTTPException(status_code=404, detail="Assigned user not found")
    item = MaintenanceRequest(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _enrich(item)


@router.patch("/{request_id}", response_model=MaintenanceRequestRead)
def update_maintenance_request(
    request_id: int,
    payload: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_module("maintenance")),
):
    item = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return _enrich(item)

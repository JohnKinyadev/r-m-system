from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import require_module, require_owner
from app.db.models.tenants import Tenant, TenantStatus
from app.db.session import get_db
from app.routers.rental_utils import current_tenancy_for_tenant, tenancy_balance
from app.schemas.tenants import TenantCreate, TenantRead, TenantUpdate

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


def _enrich(tenant: Tenant, db: Session) -> dict:
    tenancy = current_tenancy_for_tenant(db, tenant.id)
    unit = tenancy.unit if tenancy else None
    prop = unit.property if unit else None
    return {
        **{c.name: getattr(tenant, c.name) for c in Tenant.__table__.columns},
        "current_property_name": prop.name if prop else None,
        "current_unit_number": unit.unit_number if unit else None,
        "current_tenancy_id": tenancy.id if tenancy else None,
        "balance": tenancy_balance(db, tenancy.id) if tenancy else 0,
    }


@router.get("", response_model=List[TenantRead])
def list_tenants(
    q: Optional[str] = Query(None),
    status_filter: Optional[TenantStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _=Depends(require_module("tenants")),
):
    query = db.query(Tenant).order_by(Tenant.full_name)
    if status_filter:
        query = query.filter(Tenant.status == status_filter)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Tenant.full_name.ilike(term), Tenant.phone.ilike(term), Tenant.email.ilike(term)))
    return [_enrich(t, db) for t in query.all()]


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, db: Session = Depends(get_db), _=Depends(require_module("tenants"))):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return _enrich(tenant, db)


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db), _=Depends(require_module("tenants"))):
    if payload.email and db.query(Tenant).filter(Tenant.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return _enrich(tenant, db)


@router.patch("/{tenant_id}", response_model=TenantRead)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_module("tenants")),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)
    return _enrich(tenant, db)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(tenant_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    db.delete(tenant)
    db.commit()

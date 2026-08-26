from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import require_module
from app.db.models.ledger_entries import LedgerEntry, LedgerEntryType
from app.db.models.tenancies import Tenancy, TenancyStatus
from app.db.models.tenants import Tenant, TenantStatus
from app.db.models.units import Unit, UnitStatus
from app.db.session import get_db
from app.routers.rental_utils import tenancy_balance
from app.schemas.tenancies import TenancyCreate, TenancyMoveOut, TenancyRead, TenancyUpdate

router = APIRouter(prefix="/api/tenancies", tags=["tenancies"])


def _enrich(tenancy: Tenancy, db: Session) -> dict:
    unit = tenancy.unit
    prop = unit.property if unit else None
    return {
        **{c.name: getattr(tenancy, c.name) for c in Tenancy.__table__.columns},
        "tenant_name": tenancy.tenant.full_name if tenancy.tenant else None,
        "property_name": prop.name if prop else None,
        "unit_number": unit.unit_number if unit else None,
        "balance": tenancy_balance(db, tenancy.id),
    }


@router.get("", response_model=List[TenancyRead])
def list_tenancies(db: Session = Depends(get_db), _=Depends(require_module("rent"))):
    rows = db.query(Tenancy).order_by(Tenancy.start_date.desc(), Tenancy.id.desc()).all()
    return [_enrich(row, db) for row in rows]


@router.get("/{tenancy_id}", response_model=TenancyRead)
def get_tenancy(tenancy_id: int, db: Session = Depends(get_db), _=Depends(require_module("rent"))):
    tenancy = db.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    return _enrich(tenancy, db)


@router.post("", response_model=TenancyRead, status_code=status.HTTP_201_CREATED)
def create_tenancy(payload: TenancyCreate, db: Session = Depends(get_db), current_user=Depends(require_module("rent"))):
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    unit = db.query(Unit).filter(Unit.id == payload.unit_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    active = db.query(Tenancy).filter(
        Tenancy.unit_id == unit.id,
        Tenancy.status.in_([TenancyStatus.active, TenancyStatus.notice_given]),
    ).first()
    if active:
        raise HTTPException(status_code=400, detail="Unit already has an active tenancy")

    data = payload.model_dump(exclude={"opening_charge"})
    tenancy = Tenancy(**data)
    db.add(tenancy)
    unit.status = UnitStatus.occupied
    tenant.status = TenantStatus.active
    db.commit()
    db.refresh(tenancy)

    if payload.opening_charge:
        if tenancy.monthly_rent > Decimal("0"):
            db.add(LedgerEntry(
                tenancy_id=tenancy.id,
                entry_date=tenancy.start_date,
                description=f"{tenancy.start_date:%B %Y} rent",
                entry_type=LedgerEntryType.rent,
                debit=tenancy.monthly_rent,
                created_by_id=current_user.id,
            ))
        if tenancy.deposit_amount > Decimal("0"):
            db.add(LedgerEntry(
                tenancy_id=tenancy.id,
                entry_date=tenancy.start_date,
                description="Security deposit",
                entry_type=LedgerEntryType.deposit,
                debit=tenancy.deposit_amount,
                created_by_id=current_user.id,
            ))
        db.commit()
        db.refresh(tenancy)

    return _enrich(tenancy, db)


@router.patch("/{tenancy_id}", response_model=TenancyRead)
def update_tenancy(
    tenancy_id: int,
    payload: TenancyUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_module("rent")),
):
    tenancy = db.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(tenancy, field, value)
    db.commit()
    db.refresh(tenancy)
    return _enrich(tenancy, db)


@router.post("/{tenancy_id}/move-out", response_model=TenancyRead)
def move_out_tenancy(
    tenancy_id: int,
    payload: TenancyMoveOut,
    db: Session = Depends(get_db),
    _=Depends(require_module("rent")),
):
    tenancy = db.query(Tenancy).filter(Tenancy.id == tenancy_id).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    tenancy.move_out_date = payload.move_out_date
    tenancy.end_date = payload.move_out_date
    tenancy.status = TenancyStatus.ended
    tenancy.notes = payload.notes or tenancy.notes
    if tenancy.unit:
        tenancy.unit.status = UnitStatus.vacant
    if tenancy.tenant:
        tenancy.tenant.status = TenantStatus.former
    db.commit()
    db.refresh(tenancy)
    return _enrich(tenancy, db)

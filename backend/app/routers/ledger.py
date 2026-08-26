from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import require_module
from app.db.models.ledger_entries import LedgerEntry
from app.db.models.tenancies import Tenancy
from app.db.session import get_db
from app.schemas.ledger import LedgerEntryCreate, LedgerEntryRead

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


def _enrich(entry: LedgerEntry, balance_after=0) -> dict:
    tenancy = entry.tenancy
    unit = tenancy.unit if tenancy else None
    prop = unit.property if unit else None
    return {
        **{c.name: getattr(entry, c.name) for c in LedgerEntry.__table__.columns},
        "tenant_name": tenancy.tenant.full_name if tenancy and tenancy.tenant else None,
        "property_name": prop.name if prop else None,
        "unit_number": unit.unit_number if unit else None,
        "balance_after": balance_after,
    }


@router.get("", response_model=List[LedgerEntryRead])
def list_ledger_entries(
    tenancy_id: Optional[int] = Query(None),
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_module("rent")),
):
    q = db.query(LedgerEntry).join(Tenancy)
    if tenancy_id:
        q = q.filter(LedgerEntry.tenancy_id == tenancy_id)
    if tenant_id:
        q = q.filter(Tenancy.tenant_id == tenant_id)

    rows = q.order_by(LedgerEntry.entry_date, LedgerEntry.id).all()
    running = {}
    enriched = []
    for row in rows:
        balance = running.get(row.tenancy_id, 0) + row.debit - row.credit
        running[row.tenancy_id] = balance
        enriched.append(_enrich(row, balance))
    return enriched


@router.post("", response_model=LedgerEntryRead, status_code=status.HTTP_201_CREATED)
def create_ledger_entry(
    payload: LedgerEntryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_module("rent")),
):
    if not db.query(Tenancy).filter(Tenancy.id == payload.tenancy_id).first():
        raise HTTPException(status_code=404, detail="Tenancy not found")
    entry = LedgerEntry(**payload.model_dump(), created_by_id=current_user.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _enrich(entry, entry.debit - entry.credit)

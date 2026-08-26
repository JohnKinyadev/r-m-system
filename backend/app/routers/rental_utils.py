from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.ledger_entries import LedgerEntry
from app.db.models.tenancies import Tenancy, TenancyStatus


ACTIVE_TENANCY_STATUSES = [TenancyStatus.active, TenancyStatus.notice_given]


def tenancy_balance(db: Session, tenancy_id: int) -> Decimal:
    value = (
        db.query(func.coalesce(func.sum(LedgerEntry.debit - LedgerEntry.credit), 0))
        .filter(LedgerEntry.tenancy_id == tenancy_id)
        .scalar()
    )
    return value or Decimal("0")


def current_tenancy_for_unit(db: Session, unit_id: int) -> Tenancy | None:
    return (
        db.query(Tenancy)
        .filter(Tenancy.unit_id == unit_id, Tenancy.status.in_(ACTIVE_TENANCY_STATUSES))
        .order_by(Tenancy.start_date.desc(), Tenancy.id.desc())
        .first()
    )


def current_tenancy_for_tenant(db: Session, tenant_id: int) -> Tenancy | None:
    return (
        db.query(Tenancy)
        .filter(Tenancy.tenant_id == tenant_id, Tenancy.status.in_(ACTIVE_TENANCY_STATUSES))
        .order_by(Tenancy.start_date.desc(), Tenancy.id.desc())
        .first()
    )

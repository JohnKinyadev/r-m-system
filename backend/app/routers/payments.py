from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import require_module
from app.db.models.ledger_entries import LedgerEntry, LedgerEntryType
from app.db.models.payments import Payment
from app.db.models.tenancies import Tenancy
from app.db.session import get_db
from app.schemas.payments import PaymentCreate, PaymentRead

router = APIRouter(prefix="/api/payments", tags=["payments"])


def _enrich(payment: Payment) -> dict:
    tenancy = payment.tenancy
    unit = tenancy.unit if tenancy else None
    prop = unit.property if unit else None
    return {
        **{c.name: getattr(payment, c.name) for c in Payment.__table__.columns},
        "tenant_name": tenancy.tenant.full_name if tenancy and tenancy.tenant else None,
        "property_name": prop.name if prop else None,
        "unit_number": unit.unit_number if unit else None,
    }


@router.get("", response_model=List[PaymentRead])
def list_payments(db: Session = Depends(get_db), _=Depends(require_module("payments"))):
    return [_enrich(p) for p in db.query(Payment).order_by(Payment.payment_date.desc(), Payment.id.desc()).all()]


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_module("payments")),
):
    tenancy = db.query(Tenancy).filter(Tenancy.id == payload.tenancy_id).first()
    if not tenancy:
        raise HTTPException(status_code=404, detail="Tenancy not found")
    payment = Payment(**payload.model_dump(), received_by_id=current_user.id)
    db.add(payment)
    db.commit()
    db.refresh(payment)

    db.add(LedgerEntry(
        tenancy_id=tenancy.id,
        entry_date=payload.payment_date,
        description=f"Payment received from {tenancy.tenant.full_name}",
        entry_type=LedgerEntryType.payment,
        credit=payload.amount,
        reference=payload.reference,
        created_by_id=current_user.id,
        notes=payload.notes,
    ))
    db.commit()
    db.refresh(payment)
    return _enrich(payment)

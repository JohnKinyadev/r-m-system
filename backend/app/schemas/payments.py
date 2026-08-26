from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.db.models.payments import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    tenancy_id: int
    amount: Decimal
    payment_date: date
    method: PaymentMethod = PaymentMethod.cash
    reference: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    payer_phone: Optional[str] = None
    notes: Optional[str] = None


class PaymentRead(PaymentCreate):
    id: int
    status: PaymentStatus
    received_by_id: Optional[int] = None
    created_at: datetime
    tenant_name: Optional[str] = None
    property_name: Optional[str] = None
    unit_number: Optional[str] = None

    model_config = {"from_attributes": True}

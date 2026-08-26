from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, model_validator

from app.db.models.ledger_entries import LedgerEntryType


class LedgerEntryCreate(BaseModel):
    tenancy_id: int
    entry_date: date
    description: str
    entry_type: LedgerEntryType
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    reference: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def has_single_side_amount(self):
        if self.debit <= 0 and self.credit <= 0:
            raise ValueError("Ledger entry requires a debit or credit amount.")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Ledger entry cannot be both debit and credit.")
        return self


class LedgerEntryRead(LedgerEntryCreate):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    tenant_name: Optional[str] = None
    property_name: Optional[str] = None
    unit_number: Optional[str] = None
    balance_after: Decimal = Decimal("0")

    model_config = {"from_attributes": True}

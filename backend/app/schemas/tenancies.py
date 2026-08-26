from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.db.models.tenancies import TenancyStatus


class TenancyBase(BaseModel):
    tenant_id: int
    unit_id: int
    start_date: date
    end_date: Optional[date] = None
    monthly_rent: Decimal
    deposit_amount: Decimal = Decimal("0")
    rent_due_day: int = 5
    notes: Optional[str] = None


class TenancyCreate(TenancyBase):
    opening_charge: bool = True


class TenancyUpdate(BaseModel):
    end_date: Optional[date] = None
    move_out_date: Optional[date] = None
    monthly_rent: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    rent_due_day: Optional[int] = None
    status: Optional[TenancyStatus] = None
    notes: Optional[str] = None


class TenancyMoveOut(BaseModel):
    move_out_date: date
    notes: Optional[str] = None


class TenancyRead(TenancyBase):
    id: int
    move_out_date: Optional[date] = None
    status: TenancyStatus
    created_at: datetime
    tenant_name: Optional[str] = None
    property_name: Optional[str] = None
    unit_number: Optional[str] = None
    balance: Decimal = Decimal("0")

    model_config = {"from_attributes": True}

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.db.models.units import UnitStatus


class UnitBase(BaseModel):
    property_id: int
    unit_number: str
    unit_type: str
    floor: Optional[str] = None
    bedrooms: int = 1
    bathrooms: int = 1
    monthly_rent: Decimal
    deposit_amount: Decimal = Decimal("0")
    rent_due_day: int = 5
    notes: Optional[str] = None

    @field_validator("rent_due_day")
    @classmethod
    def valid_due_day(cls, v: int) -> int:
        if v < 1 or v > 31:
            raise ValueError("Rent due day must be between 1 and 31.")
        return v


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    property_id: Optional[int] = None
    unit_number: Optional[str] = None
    unit_type: Optional[str] = None
    floor: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    monthly_rent: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    rent_due_day: Optional[int] = None
    status: Optional[UnitStatus] = None
    notes: Optional[str] = None


class UnitRead(UnitBase):
    id: int
    status: UnitStatus
    created_at: datetime
    property_name: Optional[str] = None
    current_tenant_name: Optional[str] = None
    current_tenancy_id: Optional[int] = None
    balance: Decimal = Decimal("0")

    model_config = {"from_attributes": True}

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.db.models.tenants import TenantStatus


class TenantBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    national_id: Optional[str] = None
    emergency_contact: Optional[str] = None
    notes: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    national_id: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: Optional[TenantStatus] = None
    notes: Optional[str] = None


class TenantRead(TenantBase):
    id: int
    status: TenantStatus
    created_at: datetime
    current_property_name: Optional[str] = None
    current_unit_number: Optional[str] = None
    current_tenancy_id: Optional[int] = None
    balance: Decimal = Decimal("0")

    model_config = {"from_attributes": True}

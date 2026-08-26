from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.db.models.maintenance_requests import MaintenancePriority, MaintenanceStatus


class MaintenanceRequestBase(BaseModel):
    property_id: int
    unit_id: Optional[int] = None
    tenant_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: MaintenancePriority = MaintenancePriority.normal
    reported_date: date
    cost: Decimal = Decimal("0")


class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass


class MaintenanceRequestUpdate(BaseModel):
    property_id: Optional[int] = None
    unit_id: Optional[int] = None
    tenant_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[MaintenancePriority] = None
    status: Optional[MaintenanceStatus] = None
    reported_date: Optional[date] = None
    resolved_date: Optional[date] = None
    cost: Optional[Decimal] = None


class MaintenanceRequestRead(MaintenanceRequestBase):
    id: int
    status: MaintenanceStatus
    resolved_date: Optional[date] = None
    created_at: datetime
    property_name: Optional[str] = None
    unit_number: Optional[str] = None
    tenant_name: Optional[str] = None
    assigned_to_name: Optional[str] = None

    model_config = {"from_attributes": True}

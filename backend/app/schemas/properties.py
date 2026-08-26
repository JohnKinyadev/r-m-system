from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models.properties import PropertyStatus


class PropertyBase(BaseModel):
    code: str
    name: str
    property_type: str
    address: str
    city: str
    notes: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    property_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    status: Optional[PropertyStatus] = None
    notes: Optional[str] = None


class PropertyRead(PropertyBase):
    id: int
    status: PropertyStatus
    created_at: datetime
    total_units: int = 0
    occupied_units: int = 0
    vacant_units: int = 0

    model_config = {"from_attributes": True}

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models.health_logs import HealthLogType


class HealthLogCreate(BaseModel):
    animal_id: int
    log_type: HealthLogType
    description: Optional[str] = None
    weight_kg: Optional[float] = None
    vaccine_name: Optional[str] = None
    logged_at: Optional[datetime] = None


class HealthLogRead(HealthLogCreate):
    id: int
    logged_by: int
    logged_at: datetime

    model_config = {"from_attributes": True}

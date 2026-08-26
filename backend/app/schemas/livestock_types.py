from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VaccineScheduleBase(BaseModel):
    vaccine_name: str
    first_dose_age_days: int
    interval_days: Optional[int] = None


class VaccineScheduleCreate(VaccineScheduleBase):
    pass


class VaccineScheduleRead(VaccineScheduleBase):
    id: int
    livestock_type_id: int

    model_config = {"from_attributes": True}


class LivestockTypeBase(BaseModel):
    name: str
    breed: Optional[str] = None
    gestation_period_days: Optional[int] = None
    average_lifespan_years: Optional[float] = None


class LivestockTypeCreate(LivestockTypeBase):
    vaccine_schedules: List[VaccineScheduleCreate] = []


class LivestockTypeUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    gestation_period_days: Optional[int] = None
    average_lifespan_years: Optional[float] = None


class LivestockTypeRead(LivestockTypeBase):
    id: int
    created_at: datetime
    vaccine_schedules: List[VaccineScheduleRead] = []

    model_config = {"from_attributes": True}

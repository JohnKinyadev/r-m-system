from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.db.models.animals import AnimalStatus, AnimalGender


class AnimalBase(BaseModel):
    tag_number: str
    name: Optional[str] = None
    livestock_type_id: int
    gender: AnimalGender
    date_of_birth: Optional[date] = None
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    notes: Optional[str] = None


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[AnimalStatus] = None
    date_of_birth: Optional[date] = None
    notes: Optional[str] = None


class AnimalRead(AnimalBase):
    id: int
    status: AnimalStatus
    created_at: datetime
    livestock_type_name: Optional[str] = None
    age_days: Optional[int] = None
    assigned_worker_ids: list[int] = []

    model_config = {"from_attributes": True}

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class MatingEventCreate(BaseModel):
    female_id: int
    male_id: int
    mating_date: date
    notes: Optional[str] = None


class MatingEventRead(MatingEventCreate):
    id: int
    expected_birth_date: Optional[date]
    logged_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BirthCreate(BaseModel):
    mating_event_id: Optional[int] = None
    animal_id: int
    birth_date: date
    number_of_offspring: int = 1
    notes: Optional[str] = None


class BirthRead(BirthCreate):
    id: int
    logged_by: int
    created_at: datetime

    model_config = {"from_attributes": True}

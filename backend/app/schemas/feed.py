from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FeedTypeBase(BaseModel):
    name: str
    unit: str = "kg"
    low_stock_threshold: float = 50.0


class FeedTypeCreate(FeedTypeBase):
    pass


class FeedTypeUpdate(BaseModel):
    low_stock_threshold: Optional[float] = None
    unit: Optional[str] = None


class FeedTypeRead(FeedTypeBase):
    id: int
    current_stock: float
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedStockArrivalCreate(BaseModel):
    feed_type_id: int
    quantity: float
    arrived_at: datetime
    notes: Optional[str] = None


class FeedStockArrivalRead(FeedStockArrivalCreate):
    id: int
    logged_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedLogCreate(BaseModel):
    feed_type_id: int
    total_quantity: float
    session_date: datetime


class FeedDistributionRead(BaseModel):
    id: int
    animal_id: int
    quantity: float

    model_config = {"from_attributes": True}


class FeedLogRead(FeedLogCreate):
    id: int
    logged_by: int
    created_at: datetime
    distributions: List[FeedDistributionRead] = []

    model_config = {"from_attributes": True}

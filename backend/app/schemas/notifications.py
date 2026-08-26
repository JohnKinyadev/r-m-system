from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models.notifications import NotificationType


class NotificationRead(BaseModel):
    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    related_animal_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationMarkRead(BaseModel):
    ids: list[int]

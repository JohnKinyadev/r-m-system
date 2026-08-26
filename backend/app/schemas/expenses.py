from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.db.models.expenses import ExpenseCategory


class ExpenseBase(BaseModel):
    property_id: Optional[int] = None
    expense_date: date
    category: ExpenseCategory = ExpenseCategory.other
    amount: Decimal
    description: str
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    property_id: Optional[int] = None
    expense_date: Optional[date] = None
    category: Optional[ExpenseCategory] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class ExpenseRead(ExpenseBase):
    id: int
    recorded_by_id: Optional[int] = None
    created_at: datetime
    property_name: Optional[str] = None

    model_config = {"from_attributes": True}

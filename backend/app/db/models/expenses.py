from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class ExpenseCategory(str, enum.Enum):
    repairs = "repairs"
    caretaker = "caretaker"
    water = "water"
    electricity = "electricity"
    security = "security"
    garbage = "garbage"
    tax = "tax"
    other = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True, index=True)
    expense_date = Column(Date, nullable=False, index=True)
    category = Column(Enum(ExpenseCategory), default=ExpenseCategory.other, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255), nullable=False)
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="expenses")
    recorded_by = relationship("User")

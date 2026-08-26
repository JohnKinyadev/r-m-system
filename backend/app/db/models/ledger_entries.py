from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class LedgerEntryType(str, enum.Enum):
    rent = "rent"
    water = "water"
    electricity = "electricity"
    penalty = "penalty"
    deposit = "deposit"
    payment = "payment"
    adjustment = "adjustment"
    reversal = "reversal"
    credit = "credit"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    tenancy_id = Column(Integer, ForeignKey("tenancies.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)
    description = Column(String(255), nullable=False)
    entry_type = Column(Enum(LedgerEntryType), nullable=False)
    debit = Column(Numeric(12, 2), default=0, nullable=False)
    credit = Column(Numeric(12, 2), default=0, nullable=False)
    reference = Column(String(120), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancy = relationship("Tenancy", back_populates="ledger_entries")
    created_by = relationship("User")

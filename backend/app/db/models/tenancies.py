from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class TenancyStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    notice_given = "notice_given"
    ended = "ended"
    terminated = "terminated"


class Tenancy(Base):
    __tablename__ = "tenancies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    move_out_date = Column(Date, nullable=True)
    monthly_rent = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), default=0, nullable=False)
    rent_due_day = Column(Integer, default=5, nullable=False)
    status = Column(Enum(TenancyStatus), default=TenancyStatus.active, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="tenancies")
    unit = relationship("Unit", back_populates="tenancies")
    ledger_entries = relationship("LedgerEntry", back_populates="tenancy", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tenancy", cascade="all, delete-orphan")

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    mpesa = "mpesa"
    bank_transfer = "bank_transfer"
    card = "card"
    other = "other"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    reversed = "reversed"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    tenancy_id = Column(Integer, ForeignKey("tenancies.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.cash, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.confirmed, nullable=False)
    reference = Column(String(120), nullable=True)
    provider_transaction_id = Column(String(120), nullable=True)
    payer_phone = Column(String(50), nullable=True)
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancy = relationship("Tenancy", back_populates="payments")
    received_by = relationship("User")

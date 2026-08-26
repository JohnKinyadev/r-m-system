from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class HealthLogType(str, enum.Enum):
    observation = "observation"
    vaccination = "vaccination"
    treatment = "treatment"
    weight = "weight"
    deworming = "deworming"


class HealthLog(Base):
    __tablename__ = "health_logs"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    log_type = Column(Enum(HealthLogType), nullable=False)
    description = Column(Text, nullable=True)
    weight_kg = Column(Float, nullable=True)
    vaccine_name = Column(String(150), nullable=True)
    logged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    animal = relationship("Animal", back_populates="health_logs")
    logger = relationship("User")

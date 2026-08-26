from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class VaccineSchedule(Base):
    __tablename__ = "vaccine_schedules"

    id = Column(Integer, primary_key=True, index=True)
    livestock_type_id = Column(Integer, ForeignKey("livestock_types.id"), nullable=False)
    vaccine_name = Column(String(150), nullable=False)
    first_dose_age_days = Column(Integer, nullable=False)  # age in days at first dose
    interval_days = Column(Integer, nullable=True)         # repeat interval; NULL = one-time

    livestock_type = relationship("LivestockType", back_populates="vaccine_schedules")

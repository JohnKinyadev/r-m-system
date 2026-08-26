from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class AnimalStatus(str, enum.Enum):
    active = "active"
    sold = "sold"
    deceased = "deceased"


class AnimalGender(str, enum.Enum):
    male = "male"
    female = "female"


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    tag_number = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    livestock_type_id = Column(Integer, ForeignKey("livestock_types.id"), nullable=False)
    gender = Column(Enum(AnimalGender), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    mother_id = Column(Integer, ForeignKey("animals.id"), nullable=True)
    father_id = Column(Integer, ForeignKey("animals.id"), nullable=True)
    status = Column(Enum(AnimalStatus), default=AnimalStatus.active, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    livestock_type = relationship("LivestockType", back_populates="animals")
    mother = relationship("Animal", foreign_keys=[mother_id], remote_side="Animal.id")
    father = relationship("Animal", foreign_keys=[father_id], remote_side="Animal.id")
    health_logs = relationship("HealthLog", back_populates="animal", cascade="all, delete-orphan")
    feed_distributions = relationship("FeedDistribution", back_populates="animal")
    mating_events_as_female = relationship("MatingEvent", foreign_keys="MatingEvent.female_id", back_populates="female")
    mating_events_as_male = relationship("MatingEvent", foreign_keys="MatingEvent.male_id", back_populates="male")
    births = relationship("Birth", back_populates="animal")
    assignments = relationship("AnimalAssignment", back_populates="animal", cascade="all, delete-orphan")

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

# Available modules that can be granted to farm workers.
# Farm owners always have all modules; this table only applies to workers.
AVAILABLE_MODULES = [
    "animals",
    "livestock_types",
    "health",
    "feed",
    "mating",
    "reports",
]


class WorkerPermission(Base):
    __tablename__ = "worker_permissions"
    __table_args__ = (UniqueConstraint("user_id", "module", name="uq_worker_module"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module = Column(String(50), nullable=False)

    user = relationship("User", back_populates="permissions")

from sqlalchemy.orm import Session

from app.db.models.livestock_types import LivestockType
from app.db.models.roles import Role
from app.db.models.users import User

_TYPES = [
    {"name": "Cattle", "breed": "Friesian", "gestation_period_days": 280, "average_lifespan_years": 20.0},
    {"name": "Cattle", "breed": "Angus", "gestation_period_days": 285, "average_lifespan_years": 15.0},
    {"name": "Goat", "breed": "Boer", "gestation_period_days": 150, "average_lifespan_years": 12.0},
    {"name": "Sheep", "breed": "Dorper", "gestation_period_days": 147, "average_lifespan_years": 10.0},
    {"name": "Pig", "breed": "Large White", "gestation_period_days": 114, "average_lifespan_years": 15.0},
]


def seed_livestock_types(db: Session) -> None:
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()
    for lt in _TYPES:
        exists = db.query(LivestockType).filter(
            LivestockType.name == lt["name"],
            LivestockType.breed == lt["breed"],
        ).first()
        if not exists:
            db.add(LivestockType(
                name=lt["name"],
                breed=lt["breed"],
                gestation_period_days=lt["gestation_period_days"],
                average_lifespan_years=lt["average_lifespan_years"],
                created_by=owner.id,
            ))
    db.commit()

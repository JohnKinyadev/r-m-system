from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.roles import Role
from app.db.models.users import User
from app.services.seeds import (
    seed_animals,
    seed_births,
    seed_feed_logs,
    seed_feed_stock_arrivals,
    seed_feed_types,
    seed_health_logs,
    seed_livestock_types,
    seed_mating_events,
    seed_notifications,
    seed_users,
    seed_vaccine_schedules,
)


def seed_roles(db: Session) -> None:
    for name, desc in [
        ("farm_owner", "Full access to all records, reports, and configuration"),
        ("farm_worker", "Operational access: log feeds, births, health observations"),
    ]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name, description=desc))
    db.commit()


def seed_default_owner(db: Session) -> None:
    owner_role = db.query(Role).filter(Role.name == "farm_owner").first()
    if owner_role and not db.query(User).filter(User.role_id == owner_role.id).first():
        db.add(User(
            full_name=" Farm Admin",
            email="admin@farm.co.ke",
            hashed_password=hash_password("password123"),
            role_id=owner_role.id,
        ))
        db.commit()


def init_db(db: Session) -> None:
    seed_roles(db)
    seed_default_owner(db)
    seed_users(db)
    seed_livestock_types(db)
    seed_vaccine_schedules(db)
    seed_animals(db)
    seed_health_logs(db)
    seed_mating_events(db)
    seed_births(db)
    seed_feed_types(db)
    seed_feed_stock_arrivals(db)
    seed_feed_logs(db)
    seed_notifications(db)

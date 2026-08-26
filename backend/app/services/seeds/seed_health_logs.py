from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.animals import Animal
from app.db.models.health_logs import HealthLog, HealthLogType
from app.db.models.roles import Role
from app.db.models.users import User


def _animal(db: Session, tag: str) -> Animal:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def seed_health_logs(db: Session) -> None:
    worker = db.query(User).filter(User.email == "john.kamau@farm.ke").first()
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()

    logs = [
        # Friesian cattle
        HealthLog(animal_id=_animal(db, "KC001").id, log_type=HealthLogType.weight, description="Monthly weight check", weight_kg=420.5, logged_by=worker.id, logged_at=datetime(2024, 3, 1, 8, 0, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "KC001").id, log_type=HealthLogType.vaccination, vaccine_name="FMD Vaccine", description="Bi-annual FMD booster administered", logged_by=worker.id, logged_at=datetime(2024, 3, 5, 9, 30, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "KC002").id, log_type=HealthLogType.observation, description="Good coat condition, alert and active, normal milk yield", logged_by=worker.id, logged_at=datetime(2024, 3, 8, 7, 0, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "KC003").id, log_type=HealthLogType.deworming, description="Quarterly deworming treatment applied", logged_by=worker.id, logged_at=datetime(2024, 3, 10, 10, 0, tzinfo=timezone.utc)),
        # Angus cattle
        HealthLog(animal_id=_animal(db, "BC001").id, log_type=HealthLogType.weight, description="Pre-breeding season weight assessment", weight_kg=680.0, logged_by=owner.id, logged_at=datetime(2024, 3, 12, 8, 0, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "BC002").id, log_type=HealthLogType.weight, description="Post-calving weight check", weight_kg=385.0, logged_by=worker.id, logged_at=datetime(2024, 3, 25, 8, 0, tzinfo=timezone.utc)),
        # Boer goats
        HealthLog(animal_id=_animal(db, "GT001").id, log_type=HealthLogType.weight, description="Routine weight check", weight_kg=88.0, logged_by=worker.id, logged_at=datetime(2024, 3, 18, 8, 30, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "GT002").id, log_type=HealthLogType.vaccination, vaccine_name="PPR Vaccine", description="Annual PPR booster dose", logged_by=worker.id, logged_at=datetime(2024, 3, 15, 9, 0, tzinfo=timezone.utc)),
        # Dorper sheep
        HealthLog(animal_id=_animal(db, "SH001").id, log_type=HealthLogType.observation, description="Slight limping on right front leg, monitoring closely", logged_by=worker.id, logged_at=datetime(2024, 3, 20, 7, 30, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "SH002").id, log_type=HealthLogType.deworming, description="Quarterly deworming — Albendazole administered", logged_by=worker.id, logged_at=datetime(2024, 3, 22, 9, 0, tzinfo=timezone.utc)),
        # Large White pigs
        HealthLog(animal_id=_animal(db, "PG002").id, log_type=HealthLogType.treatment, description="Mild respiratory infection; amoxicillin 250 mg for 5 days", logged_by=owner.id, logged_at=datetime(2024, 3, 22, 11, 0, tzinfo=timezone.utc)),
        HealthLog(animal_id=_animal(db, "PG003").id, log_type=HealthLogType.vaccination, vaccine_name="Erysipelas Vaccine", description="Bi-annual Erysipelas booster", logged_by=worker.id, logged_at=datetime(2024, 3, 28, 10, 0, tzinfo=timezone.utc)),
    ]

    for log in logs:
        exists = db.query(HealthLog).filter(
            HealthLog.animal_id == log.animal_id,
            HealthLog.log_type == log.log_type,
            HealthLog.logged_at == log.logged_at,
        ).first()
        if not exists:
            db.add(log)
    db.commit()

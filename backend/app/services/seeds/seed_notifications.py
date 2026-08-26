from sqlalchemy.orm import Session

from app.db.models.animals import Animal
from app.db.models.notifications import Notification, NotificationType
from app.db.models.roles import Role
from app.db.models.users import User


def _animal(db: Session, tag: str) -> Animal | None:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def seed_notifications(db: Session) -> None:
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()
    john = db.query(User).filter(User.email == "john.kamau@farm.ke").first()

    notifications = [
        {
            "user_id": owner.id,
            "type": NotificationType.birth_alert,
            "title": "Upcoming Birth Alert — Nanny (GT002)",
            "message": "Nanny is expected to give birth within 7 days based on her last mating record. Prepare the kidding pen and ensure the vet is on standby.",
            "is_read": False,
            "animal_tag": "GT002",
        },
        {
            "user_id": owner.id,
            "type": NotificationType.vaccination_due,
            "title": "FMD Booster Due — Thunder (KC003)",
            "message": "Thunder's bi-annual FMD vaccination is due within 14 days. Contact the vet to schedule the visit.",
            "is_read": False,
            "animal_tag": "KC003",
        },
        {
            "user_id": owner.id,
            "type": NotificationType.feed_stock_low,
            "title": "Low Stock Alert — Goat Mineral Pellets",
            "message": "Goat Mineral Pellets stock is at 75 kg, below the reorder threshold of 80 kg. Place a restocking order soon.",
            "is_read": False,
            "animal_tag": None,
        },
        {
            "user_id": owner.id,
            "type": NotificationType.missed_feeding,
            "title": "Missed Feeding Session Detected",
            "message": "No feeding session was logged for the pig unit on 2024-03-01. Please verify with farm workers and update records.",
            "is_read": True,
            "animal_tag": None,
        },
        {
            "user_id": owner.id,
            "type": NotificationType.general,
            "title": "Monthly Health Check Reminder",
            "message": "It is time for the monthly health inspection of all livestock. Ensure weights, deworming, and observations are logged this week.",
            "is_read": True,
            "animal_tag": None,
        },
        {
            "user_id": john.id,
            "type": NotificationType.vaccination_due,
            "title": "PPR Vaccine Due — Nanny (GT002)",
            "message": "Nanny's annual PPR booster is scheduled for next week. Prepare the vaccine and log the administration in the health log after delivery.",
            "is_read": False,
            "animal_tag": "GT002",
        },
    ]

    for n in notifications:
        tag = n["animal_tag"]
        animal = _animal(db, tag) if tag else None
        exists = db.query(Notification).filter(
            Notification.user_id == n["user_id"],
            Notification.type == n["type"],
            Notification.title == n["title"],
        ).first()
        if not exists:
            db.add(Notification(
                user_id=n["user_id"],
                type=n["type"],
                title=n["title"],
                message=n["message"],
                is_read=n["is_read"],
                related_animal_id=animal.id if animal else None,
            ))
    db.commit()

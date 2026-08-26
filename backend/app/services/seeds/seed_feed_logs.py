from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.animals import Animal
from app.db.models.feed_logs import FeedDistribution, FeedLog
from app.db.models.feed_types import FeedType
from app.db.models.users import User


def _feed(db: Session, name: str) -> FeedType:
    return db.query(FeedType).filter(FeedType.name == name).first()


def _animal(db: Session, tag: str) -> Animal:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def seed_feed_logs(db: Session) -> None:
    john = db.query(User).filter(User.email == "john.kamau@farm.ke").first()
    mary = db.query(User).filter(User.email == "mary.wanjiku@farm.ke").first()

    # Each session: feed name, total kg, datetime, worker, and the animals fed
    sessions = [
        {
            "feed": "Rhodes Grass Hay",
            "total_quantity": 25.0,
            "session_date": datetime(2024, 3, 1, 8, 0, tzinfo=timezone.utc),
            "logged_by": john.id,
            "animals": ["KC001", "KC002", "KC003", "KC004", "KC005"],
        },
        {
            "feed": "Dairy Meal (16% CP)",
            "total_quantity": 15.0,
            "session_date": datetime(2024, 3, 1, 8, 30, tzinfo=timezone.utc),
            "logged_by": john.id,
            "animals": ["KC001", "KC002"],  # milking cows only
        },
        {
            "feed": "Rhodes Grass Hay",
            "total_quantity": 20.0,
            "session_date": datetime(2024, 3, 1, 17, 0, tzinfo=timezone.utc),
            "logged_by": mary.id,
            "animals": ["SH001", "SH002", "SH003", "SH004", "SH005"],
        },
        {
            "feed": "Pig Grower Pellets",
            "total_quantity": 8.0,
            "session_date": datetime(2024, 3, 2, 8, 0, tzinfo=timezone.utc),
            "logged_by": john.id,
            "animals": ["PG001", "PG002", "PG003", "PG004", "PG005"],
        },
        {
            "feed": "Maize Silage",
            "total_quantity": 50.0,
            "session_date": datetime(2024, 3, 2, 9, 0, tzinfo=timezone.utc),
            "logged_by": john.id,
            "animals": ["BC001", "BC002", "BC003", "BC004", "BC005"],
        },
        {
            "feed": "Goat Mineral Pellets",
            "total_quantity": 5.0,
            "session_date": datetime(2024, 3, 3, 8, 0, tzinfo=timezone.utc),
            "logged_by": mary.id,
            "animals": ["GT001", "GT002", "GT003", "GT004", "GT005"],
        },
    ]

    for s in sessions:
        feed = _feed(db, s["feed"])
        exists = db.query(FeedLog).filter(
            FeedLog.feed_type_id == feed.id,
            FeedLog.session_date == s["session_date"],
        ).first()
        if exists:
            continue

        feed_log = FeedLog(
            feed_type_id=feed.id,
            total_quantity=s["total_quantity"],
            session_date=s["session_date"],
            logged_by=s["logged_by"],
        )
        db.add(feed_log)
        db.flush()  # resolve feed_log.id before creating distributions

        per_animal = round(s["total_quantity"] / len(s["animals"]), 2)
        for tag in s["animals"]:
            db.add(FeedDistribution(
                feed_log_id=feed_log.id,
                animal_id=_animal(db, tag).id,
                quantity=per_animal,
            ))

    db.commit()

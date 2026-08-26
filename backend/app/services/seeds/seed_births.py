from datetime import date

from sqlalchemy.orm import Session

from app.db.models.animals import Animal
from app.db.models.births import Birth
from app.db.models.mating_events import MatingEvent
from app.db.models.roles import Role
from app.db.models.users import User


def _animal(db: Session, tag: str) -> Animal:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def _mating(db: Session, female_tag: str, male_tag: str, mating_date: date) -> MatingEvent | None:
    female = _animal(db, female_tag)
    male = _animal(db, male_tag)
    return db.query(MatingEvent).filter(
        MatingEvent.female_id == female.id,
        MatingEvent.male_id == male.id,
        MatingEvent.mating_date == mating_date,
    ).first()


def seed_births(db: Session) -> None:
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()
    worker = db.query(User).filter(User.email == "john.kamau@farm.ke").first()

    births = [
        {
            "mating": ("KC001", "KC003", date(2021, 4, 1)),
            "mother_tag": "KC001",
            "birth_date": date(2022, 1, 5),
            "offspring": 1,
            "notes": "Healthy heifer calf (Lila). Easy delivery, no complications.",
            "logged_by": worker.id,
        },
        {
            "mating": ("KC002", "KC003", date(2022, 6, 6)),
            "mother_tag": "KC002",
            "birth_date": date(2023, 4, 12),
            "offspring": 1,
            "notes": "Single heifer calf (Spot). Normal birth, good birth weight.",
            "logged_by": worker.id,
        },
        {
            "mating": ("BC002", "BC001", date(2021, 12, 1)),
            "mother_tag": "BC002",
            "birth_date": date(2022, 9, 8),
            "offspring": 1,
            "notes": "Bull calf (Junior). Strong and healthy at birth.",
            "logged_by": owner.id,
        },
        {
            "mating": ("BC003", "BC001", date(2022, 9, 13)),
            "mother_tag": "BC003",
            "birth_date": date(2023, 6, 25),
            "offspring": 1,
            "notes": "Heifer calf (Sandy). Good birth weight, attentive mother.",
            "logged_by": worker.id,
        },
        {
            "mating": ("GT002", "GT001", date(2022, 9, 30)),
            "mother_tag": "GT002",
            "birth_date": date(2023, 2, 28),
            "offspring": 2,
            "notes": "Twin kids — one doe (Kid Bella) retained, one buck sold at market.",
            "logged_by": worker.id,
        },
        {
            "mating": ("GT003", "GT001", date(2023, 2, 13)),
            "mother_tag": "GT003",
            "birth_date": date(2023, 7, 14),
            "offspring": 1,
            "notes": "Single buck kid (Kid Storm). Vigorous at birth.",
            "logged_by": worker.id,
        },
        {
            "mating": ("SH002", "SH001", date(2022, 10, 19)),
            "mother_tag": "SH002",
            "birth_date": date(2023, 3, 15),
            "offspring": 1,
            "notes": "Single ewe lamb (Lamb Rose). Healthy, nursing well.",
            "logged_by": worker.id,
        },
        {
            "mating": ("SH003", "SH001", date(2023, 3, 25)),
            "mother_tag": "SH003",
            "birth_date": date(2023, 8, 20),
            "offspring": 2,
            "notes": "Twin lambs — ram (Lamb Duke) and one ewe. Both healthy.",
            "logged_by": worker.id,
        },
        {
            "mating": ("PG002", "PG001", date(2022, 12, 17)),
            "mother_tag": "PG002",
            "birth_date": date(2023, 4, 10),
            "offspring": 8,
            "notes": "Litter of 8; 1 stillborn. 7 live piglets including Piglet Rosie.",
            "logged_by": owner.id,
        },
        {
            "mating": ("PG003", "PG001", date(2023, 5, 14)),
            "mother_tag": "PG003",
            "birth_date": date(2023, 9, 5),
            "offspring": 9,
            "notes": "Litter of 9; all live. Includes Piglet Rex. Excellent condition.",
            "logged_by": owner.id,
        },
    ]

    for b in births:
        mating = _mating(db, *b["mating"])
        mother = _animal(db, b["mother_tag"])
        exists = db.query(Birth).filter(
            Birth.animal_id == mother.id,
            Birth.birth_date == b["birth_date"],
        ).first()
        if not exists:
            db.add(Birth(
                mating_event_id=mating.id if mating else None,
                animal_id=mother.id,
                birth_date=b["birth_date"],
                number_of_offspring=b["offspring"],
                notes=b["notes"],
                logged_by=b["logged_by"],
            ))
    db.commit()

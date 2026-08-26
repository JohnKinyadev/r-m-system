from sqlalchemy.orm import Session

from app.db.models.livestock_types import LivestockType
from app.db.models.vaccine_schedules import VaccineSchedule

_SCHEDULES: dict[tuple[str, str], list[dict]] = {
    ("Cattle", "Friesian"): [
        {"vaccine_name": "FMD Vaccine", "first_dose_age_days": 90, "interval_days": 180},
        {"vaccine_name": "Lumpy Skin Disease Vaccine", "first_dose_age_days": 60, "interval_days": 365},
        {"vaccine_name": "Brucellosis Vaccine", "first_dose_age_days": 180, "interval_days": None},
        {"vaccine_name": "Blackleg Vaccine", "first_dose_age_days": 45, "interval_days": 365},
        {"vaccine_name": "Anthrax Vaccine", "first_dose_age_days": 180, "interval_days": 365},
    ],
    ("Cattle", "Angus"): [
        {"vaccine_name": "FMD Vaccine", "first_dose_age_days": 90, "interval_days": 180},
        {"vaccine_name": "Lumpy Skin Disease Vaccine", "first_dose_age_days": 60, "interval_days": 365},
        {"vaccine_name": "Blackleg Vaccine", "first_dose_age_days": 45, "interval_days": 365},
        {"vaccine_name": "Anthrax Vaccine", "first_dose_age_days": 180, "interval_days": 365},
        {"vaccine_name": "IBR Vaccine", "first_dose_age_days": 120, "interval_days": 365},
    ],
    ("Goat", "Boer"): [
        {"vaccine_name": "PPR Vaccine", "first_dose_age_days": 90, "interval_days": 365},
        {"vaccine_name": "CCPP Vaccine", "first_dose_age_days": 120, "interval_days": 365},
        {"vaccine_name": "FMD Vaccine", "first_dose_age_days": 90, "interval_days": 180},
        {"vaccine_name": "Clostridial Vaccine", "first_dose_age_days": 30, "interval_days": 365},
        {"vaccine_name": "Anthrax Vaccine", "first_dose_age_days": 180, "interval_days": 365},
    ],
    ("Sheep", "Dorper"): [
        {"vaccine_name": "PPR Vaccine", "first_dose_age_days": 90, "interval_days": 365},
        {"vaccine_name": "Clostridial Vaccine", "first_dose_age_days": 30, "interval_days": 365},
        {"vaccine_name": "FMD Vaccine", "first_dose_age_days": 90, "interval_days": 180},
        {"vaccine_name": "Anthrax Vaccine", "first_dose_age_days": 180, "interval_days": 365},
        {"vaccine_name": "Pasteurella Vaccine", "first_dose_age_days": 60, "interval_days": 180},
    ],
    ("Pig", "Large White"): [
        {"vaccine_name": "CSF Vaccine", "first_dose_age_days": 60, "interval_days": 180},
        {"vaccine_name": "FMD Vaccine", "first_dose_age_days": 90, "interval_days": 180},
        {"vaccine_name": "Erysipelas Vaccine", "first_dose_age_days": 56, "interval_days": 180},
        {"vaccine_name": "Parvovirus Vaccine", "first_dose_age_days": 180, "interval_days": 365},
        {"vaccine_name": "PRRS Vaccine", "first_dose_age_days": 21, "interval_days": 180},
    ],
}


def seed_vaccine_schedules(db: Session) -> None:
    for (name, breed), schedules in _SCHEDULES.items():
        lt = db.query(LivestockType).filter(
            LivestockType.name == name,
            LivestockType.breed == breed,
        ).first()
        if not lt:
            continue
        for s in schedules:
            exists = db.query(VaccineSchedule).filter(
                VaccineSchedule.livestock_type_id == lt.id,
                VaccineSchedule.vaccine_name == s["vaccine_name"],
            ).first()
            if not exists:
                db.add(VaccineSchedule(
                    livestock_type_id=lt.id,
                    vaccine_name=s["vaccine_name"],
                    first_dose_age_days=s["first_dose_age_days"],
                    interval_days=s["interval_days"],
                ))
    db.commit()

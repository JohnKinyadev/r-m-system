from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.db.models.animals import Animal, AnimalStatus
from app.db.models.users import User
from app.db.models.animal_assignments import AnimalAssignment
from app.schemas.animals import AnimalCreate, AnimalRead, AnimalUpdate
from app.core.dependencies import get_current_user, require_owner
from pydantic import BaseModel

router = APIRouter(prefix="/api/animals", tags=["animals"])


class AssignmentRequest(BaseModel):
    worker_ids: List[int]


def _enrich(animal: Animal, worker_ids: Optional[List[int]] = None) -> dict:
    data = {c.name: getattr(animal, c.name) for c in Animal.__table__.columns}
    data["livestock_type_name"] = animal.livestock_type.name if animal.livestock_type else None
    if animal.date_of_birth:
        data["age_days"] = (date.today() - animal.date_of_birth).days
    else:
        data["age_days"] = None
    data["assigned_worker_ids"] = worker_ids if worker_ids is not None else [
        a.worker_id for a in animal.assignments
    ]
    return data


@router.get("", response_model=List[AnimalRead])
def list_animals(
    status: Optional[AnimalStatus] = Query(None),
    livestock_type_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Animal)
    if status:
        q = q.filter(Animal.status == status)
    if livestock_type_id:
        q = q.filter(Animal.livestock_type_id == livestock_type_id)

    # Workers only see their assigned animals
    if current_user.role.name == "farm_worker":
        assigned_ids = [
            a.animal_id for a in
            db.query(AnimalAssignment).filter(AnimalAssignment.worker_id == current_user.id).all()
        ]
        q = q.filter(Animal.id.in_(assigned_ids))

    return [_enrich(a) for a in q.all()]


@router.get("/{animal_id}", response_model=AnimalRead)
def get_animal(animal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    # Workers can only view their assigned animals
    if current_user.role.name == "farm_worker":
        assigned = db.query(AnimalAssignment).filter(
            AnimalAssignment.animal_id == animal_id,
            AnimalAssignment.worker_id == current_user.id,
        ).first()
        if not assigned:
            raise HTTPException(status_code=403, detail="Not assigned to this animal")

    return _enrich(animal)


@router.post("", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(Animal).filter(Animal.tag_number == payload.tag_number).first():
        raise HTTPException(status_code=400, detail="Tag number already exists")
    animal = Animal(**payload.model_dump())
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return _enrich(animal)


@router.patch("/{animal_id}", response_model=AnimalRead)
def update_animal(
    animal_id: int,
    payload: AnimalUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(animal, field, value)
    db.commit()
    db.refresh(animal)
    return _enrich(animal)


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(animal_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    db.delete(animal)
    db.commit()


# ── Assignment endpoints ──────────────────────────────────────────────────────

@router.get("/{animal_id}/workers", response_model=List[int])
def get_assigned_workers(animal_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    """Return the list of worker IDs assigned to this animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return [a.worker_id for a in animal.assignments]


@router.put("/{animal_id}/workers", response_model=List[int])
def set_assigned_workers(
    animal_id: int,
    payload: AssignmentRequest,
    db: Session = Depends(get_db),
    _=Depends(require_owner),
):
    """Replace the worker assignment for this animal (owner only)."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    # Validate all worker IDs exist and are actual workers
    for wid in payload.worker_ids:
        worker = db.query(User).filter(User.id == wid).first()
        if not worker:
            raise HTTPException(status_code=404, detail=f"User {wid} not found")
        if worker.role.name != "farm_worker":
            raise HTTPException(status_code=400, detail=f"User {wid} is not a farm worker")

    db.query(AnimalAssignment).filter(AnimalAssignment.animal_id == animal_id).delete()
    for wid in payload.worker_ids:
        db.add(AnimalAssignment(animal_id=animal_id, worker_id=wid))
    db.commit()
    db.refresh(animal)
    return [a.worker_id for a in animal.assignments]

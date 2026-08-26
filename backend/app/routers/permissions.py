from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.permissions import WorkerPermission, AVAILABLE_MODULES
from app.core.dependencies import require_owner
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["permissions"])


class PermissionSet(BaseModel):
    modules: List[str]


@router.get("/{user_id}/permissions", response_model=List[str])
def get_permissions(user_id: int, db: Session = Depends(get_db), _=Depends(require_owner)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [p.module for p in user.permissions]


@router.put("/{user_id}/permissions", response_model=List[str])
def set_permissions(
    user_id: int,
    payload: PermissionSet,
    db: Session = Depends(get_db),
    _=Depends(require_owner),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role.name == "landlord":
        raise HTTPException(status_code=400, detail="Landlords always have full access - no per-module permissions needed")

    invalid = [m for m in payload.modules if m not in AVAILABLE_MODULES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unknown modules: {invalid}. Valid: {AVAILABLE_MODULES}")

    db.query(WorkerPermission).filter(WorkerPermission.user_id == user_id).delete()
    for module in payload.modules:
        db.add(WorkerPermission(user_id=user_id, module=module))
    db.commit()
    db.refresh(user)
    return [p.module for p in user.permissions]

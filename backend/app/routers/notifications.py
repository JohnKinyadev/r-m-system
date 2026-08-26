from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.notifications import Notification
from app.db.models.users import User
from app.schemas.notifications import NotificationRead, NotificationMarkRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationRead])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.patch("/mark-read")
def mark_read(payload: NotificationMarkRead, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.id.in_(payload.ids),
        Notification.user_id == current_user.id,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"marked": len(payload.ids)}


@router.patch("/mark-all-read")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read"}

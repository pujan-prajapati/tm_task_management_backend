from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.notifications.models import NotificationModel
from src.users.models import UserModel

from src.utils.helpers import success_response


# ================== CREATE NOTIFICATION ===========================
def create_notification(message: str, user_id: int, db: Session):
    notification = NotificationModel(message=message, user_id=user_id)

    db.add(notification)

    return notification


# ================== GET MY NOTIFICATION ===========================
def get_my_notification(db: Session, user: UserModel):
    query = (
        select(NotificationModel)
        .where(NotificationModel.user_id == user.id)
        .order_by(NotificationModel.created_at.desc())
    )

    notifications = db.scalars(query).all()

    return success_response(
        data=notifications, message="Notification Fetched Successfully"
    )


# ==================== MARK NOTIFICATION AS READ ======================
def mark_notification_as_read(notification_id: int, db: Session, user: UserModel):
    notification = db.get(NotificationModel, notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification Not Found"
        )

    if notification.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return success_response(data=notification, message="Notification Marked As Read")

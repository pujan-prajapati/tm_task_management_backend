from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.notifications import controllers
from src.notifications.dtos import NotificationResponseSchema
from src.dependencies.is_authenticated import is_authenticated
from src.users.models import UserModel
from src.utils.dtos import ResponseSchema

notification_routes = APIRouter(prefix="/notifications", tags=["Notifications"])


# ================= GET MY NOTIFICATIONS =============================
@notification_routes.get(
    "/",
    response_model=ResponseSchema[list[NotificationResponseSchema]],
    status_code=status.HTTP_200_OK,
)
def get_my_notifications(
    db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)
):
    return controllers.get_my_notification(db, user)


# ================= MARK NOTIFICATION AS READ =============================
@notification_routes.patch(
    "/{notification_id}/read",
    response_model=ResponseSchema[NotificationResponseSchema],
    status_code=status.HTTP_200_OK,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.mark_notification_as_read(notification_id, db, user)

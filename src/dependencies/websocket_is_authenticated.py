from fastapi import WebSocket
from src.users.models import UserModel
from src.core.settings import settings
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
from jwt.exceptions import InvalidTokenError
import jwt


# ===================== WEBSOCKET IS AUTHENTICATED =======================================
def websocket_is_authenticated(websocket: WebSocket, db: Session):
    try:
        token = websocket.query_params.get("token")

        if not token:
            raise InvalidTokenError

        data = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

        user_id = data.get("_id")

        if not user_id:
            raise InvalidTokenError

        user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            raise InvalidTokenError

        if not user.is_active:
            raise InvalidTokenError

        return user

    except InvalidTokenError:
        raise None

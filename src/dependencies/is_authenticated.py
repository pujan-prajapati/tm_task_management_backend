from fastapi import Request, HTTPException, status, Depends
from src.users.models import UserModel
from src.core.settings import settings
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
from src.core.db import get_db
from jwt.exceptions import InvalidTokenError
import jwt


# ===================== IS AUTHENTICATED =======================================
def is_authenticated(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="You Are Unauthorized"
            )

        token = token.split(" ")[-1]

        data = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

        user_id = data.get("_id")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="You Are Unauthorized"
            )

        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You Are Unauthorized"
        )

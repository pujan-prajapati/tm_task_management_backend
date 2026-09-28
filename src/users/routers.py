from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
    BackgroundTasks,
)
from sqlalchemy.orm import Session

from src.users.dtos import (
    UserSchema,
    UserResponseSchema,
    LoginSchema,
    LoginResponseSchema,
    AvatarResponseSchema,
)
from src.users import controllers

from src.core.db import get_db

from src.dependencies.is_authenticated import is_authenticated

from src.users.models import UserModel
from src.utils.dtos import SuccessResponse

user_routes = APIRouter(prefix="/users")


# =============== register user ==========================
@user_routes.post(
    "/register",
    response_model=SuccessResponse[UserResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: UserSchema, bg_task: BackgroundTasks, db: Session = Depends(get_db)
):
    return await controllers.register(body, bg_task, db)


# =============== login user ==============================
@user_routes.post(
    "/login",
    response_model=SuccessResponse[LoginResponseSchema],
    status_code=status.HTTP_200_OK,
)
def login(body: LoginSchema, db: Session = Depends(get_db)):
    return controllers.login(body, db)


# =============== upload avatar ==============================
@user_routes.post(
    "/upload-avatar",
    response_model=SuccessResponse[AvatarResponseSchema],
    status_code=status.HTTP_200_OK,
)
def upload_avatar(
    file: UploadFile = File(...),
    user: UserModel = Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    return controllers.upload_avatar(file, user, db)

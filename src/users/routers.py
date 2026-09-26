from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from src.users.dtos import UserSchema, UserResponseSchema, LoginSchema
from src.users import controllers
from src.utils.db import get_db
from src.utils.helpers import is_authenticated
from src.users.models import UserModel

user_routes = APIRouter(prefix="/users")


# =============== register user ==========================
@user_routes.post(
    "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register(
    body: UserSchema, bg_task: BackgroundTasks, db: Session = Depends(get_db)
):
    return await controllers.register(body, bg_task, db)


# =============== login user ==============================
@user_routes.post("/login", status_code=status.HTTP_200_OK)
def login(body: LoginSchema, db: Session = Depends(get_db)):
    return controllers.login(body, db)


# =============== upload avatar ==============================
@user_routes.post("/upload-avatar", status_code=status.HTTP_200_OK)
def upload_avatar(
    file: UploadFile = File(...),
    user: UserModel = Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    return controllers.upload_avatar(file, user, db)

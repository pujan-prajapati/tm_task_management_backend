from fastapi import APIRouter, Depends, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.users.dtos import UserSchema, UserResponseSchema, LoginSchema
from src.users import controllers
from src.utils.db import get_db

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


# is authenticated
@user_routes.get(
    "/is_auth", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
def is_auth(request: Request, db: Session = Depends(get_db)):
    return controllers.is_authenticated(request, db)

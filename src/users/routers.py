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
    UpdateUserRoleSchema,
    UpdateUserStatusSchema,
)
from src.users import controllers

from src.core.db import get_db

from src.dependencies.is_authenticated import is_authenticated
from src.dependencies.check_admin import admin_required

from src.users.models import UserModel
from src.utils.dtos import ResponseSchema

user_routes = APIRouter(prefix="/users", tags=["Users"])


# =============== register user ==========================
@user_routes.post(
    "/register",
    response_model=ResponseSchema[UserResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
async def register(body: UserSchema, db: Session = Depends(get_db)):
    return await controllers.register(body, db)


# =============== login user ==============================
@user_routes.post(
    "/login",
    response_model=ResponseSchema[LoginResponseSchema],
    status_code=status.HTTP_200_OK,
)
def login(body: LoginSchema, db: Session = Depends(get_db)):
    return controllers.login(body, db)


# =============== login user ==============================
@user_routes.get("/me")
def current_user(
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_current_user(user)


# =============== upload avatar ==============================
@user_routes.post(
    "/upload-avatar",
    response_model=ResponseSchema[AvatarResponseSchema],
    status_code=status.HTTP_200_OK,
)
def upload_avatar(
    file: UploadFile = File(...),
    user: UserModel = Depends(is_authenticated),
    db: Session = Depends(get_db),
):
    return controllers.upload_avatar(file, user, db)


# =============== GET ALL USERS ==============================
@user_routes.get(
    "/admin/users", response_model=ResponseSchema[list[UserResponseSchema]]
)
def get_users(db: Session = Depends(get_db), user: UserModel = Depends(admin_required)):
    return controllers.get_all_users(db, user)


# =============== UPDATE USER ROLE ==============================
@user_routes.put(
    "/admin/users/{user_id}/role",
    response_model=ResponseSchema[UserResponseSchema],
)
def update_role(
    user_id: int,
    body: UpdateUserRoleSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(admin_required),
):
    return controllers.update_user_role(user_id, body, db, user)


# =============== ADMIN ACTIVATE/DEACTIVATE ==============================
@user_routes.patch(
    "/admin/users/{user_id}/status",
    response_model=ResponseSchema[UserResponseSchema],
)
def update_status(
    user_id: int,
    body: UpdateUserStatusSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(admin_required),
):
    return controllers.update_user_status(
        user_id,
        body,
        db,
        user,
    )


# ============= DELETE USER =================================
@user_routes.delete(
    "/admin/users/{user_id}",
    response_model=ResponseSchema[None],
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(admin_required),
):
    return controllers.delete_user(
        user_id,
        db,
        user,
    )

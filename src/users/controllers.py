from fastapi import HTTPException, status, BackgroundTasks, UploadFile
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.settings import settings

from src.utils.mail import send_email
from src.utils.upload import save_file, delete_file
from src.utils.helpers import success_response
from src.users.dtos import (
    UserSchema,
    LoginSchema,
    UpdateUserRoleSchema,
    UpdateUserStatusSchema,
)
from src.users.models import UserModel

import jwt
from pwdlib import PasswordHash

from src.utils.redis import increment_counter, delete_cache, get_cache
from src.jobs.email_jobs import send_email_job
from src.jobs.queue import email_queue, email_retry

password_hash = PasswordHash.recommended()


# ============== password hash function ============================
def get_password_hash(password):
    return password_hash.hash(password)


# ============= verfiy password function ===============================
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# ============= register user ===================================
async def register(body: UserSchema, db: Session):
    # check if user already exists with username
    query = select(UserModel).where(UserModel.username == body.username)
    user = db.scalar(query)

    if user:
        raise HTTPException(400, detail="Username Already Exists")

    # check if user already exists with email
    query = select(UserModel).where(UserModel.email == body.email)
    email = db.scalar(query)

    if email:
        raise HTTPException(400, detail="Email Already Exists")

    # check if phone already exists or not
    query = select(UserModel).where(UserModel.phone == body.phone)
    phone = db.scalar(query)

    if phone:
        raise HTTPException(400, detail="Phone Already Exists")

    # hash password
    hash_password = get_password_hash(body.password)

    # create new user
    new_user = UserModel(
        name=body.name,
        username=body.username,
        email=body.email,
        hash_password=hash_password,
        phone=body.phone,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # send email confirmation
    html = """<p>Hi, Thanks for Registration, Our team will contact you soon!</p> """
    subject = "Registration Confirmation"
    email_queue.enqueue(
        send_email_job,
        emails=[new_user.email],
        subject=subject,
        html=html,
        retry=email_retry,
    )
    # bg_task.add_task(send_email, [new_user.email], subject=subject, html=html)

    return success_response(new_user, "User Registered Successful")


# ============= login user ==================================
def login(body: LoginSchema, db: Session):
    rate_limit_key = f"login_attemts:{body.username}"

    attempts = get_cache(rate_limit_key)

    if attempts is not None and int(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later",
        )

    # check if user exists or not
    query = select(UserModel).where(UserModel.username == body.username)
    user = db.scalar(query)

    if not user:
        increment_counter(rate_limit_key, 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not verify_password(body.password, user.hash_password):
        increment_counter(rate_limit_key, 60)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User Account Is Inactive"
        )

    delete_cache(rate_limit_key)

    exp_time = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = jwt.encode(
        {"_id": user.id, "exp": exp_time.timestamp()},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    return success_response({"token": token}, "Login Successful")


# ============= GET CURRENT USER =================================
def get_current_user(user: UserModel):
    return success_response(
        data=user,
        message="Current User Fetched Successfully",
    )


# ============= upload avatar =================================
def upload_avatar(file: UploadFile, user: UserModel, db: Session):
    if user.avatar:

        delete_file(user.avatar, "media/avatars")

    filename = save_file(
        file=file,
        folder="media/avatars",
    )

    user.avatar = filename

    db.commit()
    db.refresh(user)

    return success_response({"avatar": filename}, "Avatar uploaded successfully")


# ============= GET ALL USERS =================================
def get_all_users(db: Session, user: UserModel):
    users = db.scalars(select(UserModel)).all()

    return success_response(data=users, message="Users Fetched Successfully")


# ============= UPDATE USER ROLE =================================
def update_user_role(
    user_id: int, body: UpdateUserRoleSchema, db: Session, current_user: UserModel
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    user = db.get(UserModel, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    user.role = body.role

    db.commit()
    db.refresh(user)

    return success_response(data=user, message="User Role Updated Successfully")


# ============= ADMIN ACTIVATE/DEACTIVATE =================================
def update_user_status(
    user_id: int, body: UpdateUserStatusSchema, db: Session, current_user: UserModel
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own status",
        )

    user = db.get(UserModel, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    user.is_active = body.is_active

    db.commit()
    db.refresh(user)

    return success_response(data=user, message="User Status Updated Successfully")


# ============= DELETE USER =================================
def delete_user(
    user_id: int,
    db: Session,
    current_user: UserModel,
):
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = db.get(UserModel, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found",
        )

    db.delete(user)
    db.commit()

    return success_response(
        data=None,
        message="User Deleted Successfully",
    )

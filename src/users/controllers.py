from fastapi import HTTPException, status, BackgroundTasks, UploadFile
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.settings import settings

from src.utils.mail import send_email
from src.utils.upload import save_file, delete_file
from src.utils.helpers import success_response
from src.users.dtos import UserSchema, LoginSchema
from src.users.models import UserModel

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


# ============== password hash function ============================
def get_password_hash(password):
    return password_hash.hash(password)


# ============= verfiy password function ===============================
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# ============= register user ===================================
async def register(body: UserSchema, bg_task: BackgroundTasks, db: Session):
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
    bg_task.add_task(send_email, [new_user.email])

    return success_response(new_user, "User registered successfully")


# ============= login user ==================================
def login(body: LoginSchema, db: Session):
    # check if user exists or not
    query = select(UserModel).where(UserModel.username == body.username)
    user = db.scalar(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not verify_password(body.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    exp_time = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = jwt.encode(
        {"_id": user.id, "exp": exp_time.timestamp()},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    return success_response({"token": token}, "Login successful")


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

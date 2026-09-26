from fastapi import HTTPException, status, BackgroundTasks
from src.users.dtos import UserSchema
from sqlalchemy.orm import Session
from src.users.models import UserModel
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime, timedelta
from src.utils.mail import send_email
import jwt

password_hash = PasswordHash.recommended()


# password hash function
def get_password_hash(password):
    return password_hash.hash(password)


# verfiy password function
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# register user
async def register(body: UserSchema, bg_task: BackgroundTasks, db: Session):
    # check if user already exists with username
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if user:
        raise HTTPException(400, detail="Username Already Exists")

    # check if user already exists with email
    email = db.query(UserModel).filter(UserModel.email == body.email).first()
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

    return new_user


# login user
def login(body: UserSchema, db: Session):
    # check if user exists or not
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
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

    return {"token": token}

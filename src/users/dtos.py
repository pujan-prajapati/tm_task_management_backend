from pydantic import BaseModel, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserSchema(BaseModel):
    name: str
    username: str
    password: str
    email: str
    phone: str


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    username: str
    email: str
    phone: str
    role: str
    is_active: bool


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginResponseSchema(BaseModel):
    token: str


class AvatarResponseSchema(BaseModel):
    avatar: str


class UpdateUserRoleSchema(BaseModel):
    role: UserRole


class UpdateUserStatusSchema(BaseModel):
    is_active: bool

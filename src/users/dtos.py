from pydantic import BaseModel


class UserSchema(BaseModel):
    name: str
    username: str
    password: str
    email: str
    phone: str


class UserResponseSchema(BaseModel):
    name: str
    username: str
    email: str
    phone: str


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginResponseSchema(BaseModel):
    token: str


class AvatarResponseSchema(BaseModel):
    avatar: str

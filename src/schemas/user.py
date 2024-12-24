from pydantic import BaseModel, EmailStr
from src.schemas.enums import UserRoleEnum


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserBase(BaseModel):
    login: str
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRoleEnum


class UserCreate(UserBase):
    password: str


class UserDetail(BaseModel):
    id: int
    name: str
    email: str

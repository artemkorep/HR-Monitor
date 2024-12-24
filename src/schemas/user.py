from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time, timedelta
from enum import Enum
from src.schemas.enums import UserRoleEnum, StageEnum


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserBase(BaseModel):
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

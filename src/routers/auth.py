import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from src.core.db.database import get_db
from fastapi.responses import JSONResponse
from src.models.models import User, UserRoleEnum
from src.schemas.schemas import UserCreate, Token
from src.core.db.database import session_local
from src.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", summary="Регистрация нового пользователя")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    try:
        role = UserRoleEnum(user.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректная роль пользователя")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login", response_model=Token, summary="Авторизация пользователя")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Некорректный email или пароль")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    response = JSONResponse(content={"message": "Успешная авторизация"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
    )
    return response

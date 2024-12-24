from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from src.core.db.database import get_db
from src.models.models import User, UserRoleEnum
from src.schemas import AuthResponse, UserCreate, UserBase
from src.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.post("/register", summary="Register new user")
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserBase:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    try:
        role = UserRoleEnum(user.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректная роль пользователя")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        login=user.login,
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
    return UserBase(
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
    )


@router.post("/login", summary="Login in account")
async def login(
    login: str,
    password: str,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = db.query(User).filter(User.login == login).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Некорректный email или пароль")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="lax",
    )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", summary="Logout into account")
async def logout(response: Response) -> None:
    response.delete_cookie(key="access")

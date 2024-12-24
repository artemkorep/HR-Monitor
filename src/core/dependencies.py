from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from src.models.models import UserRoleEnum
from fastapi import Cookie
from sqlalchemy.orm import Session
from src.models.models import User
from src.core.db.database import get_db
from pydantic import ValidationError
from src.settings import settings


def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Токен отсутствует")

    try:
        token = access_token.replace("Bearer ", "")

        payload = jwt.decode(
            token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Неверный токен")

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    except (JWTError, ValidationError) as e:
        raise HTTPException(status_code=401, detail="Неверный токен")


def check_team_lead(current_user: dict = Depends(get_current_user)):
    if (current_user.role != UserRoleEnum.team_lead) and (
        current_user.role != UserRoleEnum.admin
    ):
        raise HTTPException(
            status_code=403, detail="Доступ только для Team Leader: недостаточно прав"
        )
    return current_user


def check_admin(current_user: dict = Depends(get_current_user)):
    if not (current_user.role == UserRoleEnum.admin):
        raise HTTPException(
            status_code=403, detail="Доступ кандидатам запрещен: недостаточно прав"
        )
    return check_admin


def check_hr(current_user: dict = Depends(get_current_user)):
    if not (
        (current_user.role == UserRoleEnum.hr)
        or (current_user.role == UserRoleEnum.team_lead)
        or (current_user.role == UserRoleEnum.admin)
    ):
        raise HTTPException(
            status_code=403, detail="Доступ кандидатам запрещен: недостаточно прав"
        )
    return current_user


def check_candidate(current_user: dict = Depends(get_current_user)):
    if not (
        (current_user.role == UserRoleEnum.candidate)
        or (current_user.role == UserRoleEnum.team_lead)
        or (current_user.role == UserRoleEnum.admin)
    ):
        raise HTTPException(
            status_code=403, detail="Доступ HR запрещен: недостаточно прав"
        )
    return current_user

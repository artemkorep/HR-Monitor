from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from src.models.models import UserRoleEnum
from fastapi import Cookie
from sqlalchemy.orm import Session
from src.models.models import User
from src.core.db.database import get_db
from pydantic import ValidationError


SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    print(f"Токен из Cookie: {access_token}")  # Логируем токен из Cookie

    if not access_token:
        print("Токен отсутствует!")  # Логируем отсутствие токена
        raise HTTPException(status_code=401, detail="Токен отсутствует")

    try:
        # Убираем "Bearer " из токена, если оно есть
        token = access_token.replace("Bearer ", "")
        print(f"Токен после очистки: {token}")  # Логируем токен без Bearer

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload из токена: {payload}")  # Логируем содержимое токена

        email: str = payload.get("sub")
        if email is None:
            print("Email отсутствует в токене!")  # Логируем отсутствие email
            raise HTTPException(status_code=401, detail="Неверный токен")
        
        # Проверяем пользователя в базе
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print("Пользователь не найден!")  # Логируем отсутствие пользователя
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        print(f"Пользователь найден: {user.email}")  # Логируем найденного пользователя
        return user
    except (JWTError, ValidationError) as e:
        print(f"Ошибка токена: {str(e)}")  # Логируем ошибки
        raise HTTPException(status_code=401, detail="Неверный токен")



# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email = payload.get("sub")
#         role = payload.get("role")
#         if email is None or role is None:
#             raise HTTPException(status_code=401, detail="Некорректный токен")
#         return {"email": email, "role": role}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Некорректный токен")


def check_role(required_role: UserRoleEnum):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role.value:
            raise HTTPException(status_code=403, detail="Доступ запрещен: недостаточно прав")
        return current_user
    return role_checker

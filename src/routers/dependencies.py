from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from src.models.models import UserRoleEnum

# Конфигурация для JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Зависимость для OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Получение текущего пользователя из токена
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Некорректный токен")
        return {"email": email, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Некорректный токен")

# Проверка роли пользователя
def check_role(required_role: UserRoleEnum):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role.value:
            raise HTTPException(status_code=403, detail="Доступ запрещен: недостаточно прав")
        return current_user
    return role_checker

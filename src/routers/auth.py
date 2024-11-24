from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.models.models import User, UserRoleEnum
from src.schemas.schemas import UserCreate, Token
from src.core.db.database import session_local

# Конфигурация для JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Роутер
router = APIRouter()

# Зависимость для получения сессии базы данных
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Генерация токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Регистрация пользователя
@router.post("/register", summary="Регистрация нового пользователя")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверка, существует ли пользователь
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Хэшируем пароль и создаем нового пользователя
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Пользователь успешно зарегистрирован"}

# Аутентификация пользователя
@router.post("/login", response_model=Token, summary="Авторизация пользователя")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    # Проверка существования пользователя
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Некорректный email или пароль")

    # Генерация токена
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

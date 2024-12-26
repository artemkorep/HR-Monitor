from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.core.db.database import Base, engine
from src.routers import router
from src.schemas import UserRoleEnum
from datetime import datetime
from src.core.db.database import get_db, session_local
from src.models.models import User


app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0",
)
app.include_router(router)

Base.metadata.create_all(bind=engine)

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

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def create_supervisor(db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(User.role == UserRoleEnum.admin).first()
    if not admin_exists:
        hashed_password = CryptContext(schemes=["bcrypt"]).hash("admin")
        new_admin = User(
            login="admin",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            role=UserRoleEnum.admin,
            created_at=datetime.utcnow(),
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Admin user created!")


@app.on_event("startup")
def on_startup():
    db = session_local()
    try:
        create_supervisor(db)
    finally:
        db.close()

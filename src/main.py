from fastapi import FastAPI, Depends, Request
from src.core.db.database import Base, engine
from src.routers import auth, statistics, resumes, vacancies, sla
from src.core.security import JWTBearer
from src.routers.dependencies import get_current_user
from src.models.models import User


app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0",
)


jwt_scheme = JWTBearer()

app.include_router(auth.router, prefix="/auth", tags=["Authorization"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])
app.include_router(sla.router, prefix="/sla", tags=["SLA"])


Base.metadata.create_all(bind=engine)

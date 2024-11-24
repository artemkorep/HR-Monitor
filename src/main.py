from fastapi import FastAPI
from src.core.db.database import Base, engine
from src.routers import auth, statistics, resumes, vacancies, sla


# Создаем объект приложения
app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0"
)

# Подключаем маршруты
app.include_router(auth.router, prefix="/auth", tags=["Authorization"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])
app.include_router(sla.router, prefix="/sla", tags=["SLA"])

# Создаем таблицы в базе данных (если их нет)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to HR Monitor API"}

from fastapi import FastAPI, Depends
from src.core.db.database import Base, engine
from src.routers import auth, statistics, resumes, vacancies, sla
from src.core.security import JWTBearer
from src.core.openapi_config import custom_openapi

# Создаем объект приложения
app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0",
)

# JWT Security
jwt_scheme = JWTBearer()

# Подключаем маршруты
app.include_router(auth.router, prefix="/auth", tags=["Authorization"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["Vacancies"])
app.include_router(sla.router, prefix="/sla", tags=["SLA"])

# Создаем таблицы в базе данных (если их нет)
Base.metadata.create_all(bind=engine)

# Настройка OpenAPI
app.openapi = lambda: custom_openapi(app)

# Тестовый защищённый маршрут
@app.get("/protected-route", tags=["Protected"])
async def protected_route(token: str = Depends(jwt_scheme)):
    return {"message": "You have accessed a protected route!", "token": token}

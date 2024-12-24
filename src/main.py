from fastapi import FastAPI
from src.core.db.database import Base, engine
from src.routers import router


app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0",
)
app.include_router(router)

Base.metadata.create_all(bind=engine)

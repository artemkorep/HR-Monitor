from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Подключение к базе данных
SQLDBURL = os.getenv("DATABASE_URL")

engine = create_engine(SQLDBURL)
session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

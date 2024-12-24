from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    DateTime,
    Time,
    Boolean,
    Interval,
)
from sqlalchemy.orm import relationship
from src.core.db.database import Base
from src.models.enums import StageEnum, ResumesSourceEnum, UserRoleEnum


class Resume(Base):
    __tablename__ = "resumes"

    id_resume = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id_user"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.id_vacancy"))
    source = Column(Enum(ResumesSourceEnum))
    current_stage = Column(Enum(StageEnum))
    sla_time = Column(Time)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User")
    vacancy = relationship("Vacancy")


class Vacancy(Base):
    __tablename__ = "vacancies"

    id_vacancy = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)


class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRoleEnum), nullable=False)
    created_at = Column(DateTime, nullable=False)


class SLASettings(Base):
    __tablename__ = "sla_settings"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Enum(StageEnum), unique=True, nullable=False)
    sla_duration = Column(Interval, nullable=False)

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
from datetime import datetime
from src.schemas import StageEnum, ResumesSourceEnum, UserRoleEnum


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"))
    source = Column(Enum(ResumesSourceEnum))
    current_stage = Column(Enum(StageEnum))
    sla_time = Column(Time)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User")
    vacancy = relationship("Vacancy")


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRoleEnum), nullable=False)
    created_at = Column(DateTime, nullable=False)


class UserTeamLead(Base):
    __tablename__ = "user_team_leads"

    hr_user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    team_lead_user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    hr_user = relationship("User", foreign_keys=[hr_user_id])
    team_lead_user = relationship("User", foreign_keys=[team_lead_user_id])


class SLASettings(Base):
    __tablename__ = "sla_settings"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Enum(StageEnum), unique=True, nullable=False)
    sla_duration = Column(Interval, nullable=False)

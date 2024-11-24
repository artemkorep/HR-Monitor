from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Time, Boolean
from sqlalchemy.orm import relationship
from src.core.db.database import Base
import enum

# Существующий перечисления стадий
class StageEnum(enum.Enum):
    open = "open"
    reviewed = "reviewed"
    interview = "interview"
    passed_interview = "passed_interview"
    tech_interview = "tech_interview"
    passed_tech_interview = "passed_tech_interview"
    offer = "offer"

class ResumesSourceEnum(enum.Enum):
    LinkedIn = "LinkedIn"
    Email = "Email"
    JobBoard = "JobBoard"
    Referral = "Referral"

# Добавление ролей пользователей
class UserRoleEnum(enum.Enum):
    hr = "HR"
    team_lead = "HR Team Lead"

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
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.hr)  # Добавление роли
    created_at = Column(DateTime)

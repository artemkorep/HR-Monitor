from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time, timedelta
from enum import Enum
from src.models.enums import UserRoleEnum, StageEnum

# Источники резюме
class ResumesSourceEnum(str, Enum):
    LinkedIn = "LinkedIn"
    Email = "Email"
    JobBoard = "JobBoard"
    Referral = "Referral"

# Базовая схема резюме
class ResumeBase(BaseModel):
    user_id: int
    vacancy_id: int
    source: ResumesSourceEnum
    current_stage: StageEnum
    sla_time: Optional[time]
    created_at: datetime
    updated_at: datetime

class Resume(ResumeBase):
    id_resume: int

    class Config:
        from_attributes = True

class ResumeFilter(BaseModel):
    stage: Optional[StageEnum]
    vacancy_id: Optional[int]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
    from_sla: Optional[time]
    to_sla: Optional[time]
    sort_by_date: Optional[bool] = True
    sort_by_sla: Optional[bool] = False

# Схемы пользователей
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRoleEnum

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id_user: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Схема для создания вакансии
class VacancyCreate(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes = True

# Обновление SLA
class SLAUpdate(BaseModel):
    stage: StageEnum
    sla_duration: timedelta  # Время в формате "1 day", "2 hours", etc.

class SLAViolation(BaseModel):
    resume_id: int
    stage: StageEnum
    time_exceeded: timedelta

class SLAResponse(BaseModel):
    violations: List[SLAViolation]

# Запрос для SLA-отчета
class SLAReportRequest(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    stage: Optional[StageEnum] = None
    user_id: Optional[int] = None  # Фильтр по HR

# Детализация нарушения SLA
class SLAViolationDetail(BaseModel):
    resume_id: int
    user: str
    stage: StageEnum
    time_exceeded: timedelta

# Ответ SLA-отчета
class SLAReportResponse(BaseModel):
    total_violations: int
    violations_detail: List[SLAViolationDetail]

# Ответ для проверки SLA
class SLAResponse(BaseModel):
    violations: List[SLAViolationDetail]

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime, time


class StageEnum(str, Enum):
    open = "open"
    reviewed = "reviewed"
    interview = "interview"
    passed_interview = "passed_interview"
    tech_interview = "tech_interview"
    passed_tech_interview = "passed_tech_interview"
    offer = "offer"

class ResumesSourceEnum(str, Enum):
    LinkedIn = "LinkedIn"
    Email = "Email"
    JobBoard = "JobBoard"
    Referral = "Referral"



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
        orm_mode = True



class ResumeFilter(BaseModel):
    stage: Optional[StageEnum]
    vacancy_id: Optional[int]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
    from_sla: Optional[time]
    to_sla: Optional[time]
    sort_by_date: Optional[bool] = True
    sort_by_sla: Optional[bool] = False


class VacancyBase(BaseModel):
    title: str
    description: str

class VacancyCreate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id_vacancy: int

    class Config:
        orm_mode = True

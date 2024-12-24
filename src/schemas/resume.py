from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
from src.schemas.enums import StageEnum, ResumesSourceEnum


class ResumeFilter(BaseModel):
    stage: Optional[StageEnum]
    vacancy_id: Optional[int]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
    from_sla: Optional[time]
    to_sla: Optional[time]
    sort_by_date: Optional[bool] = True
    sort_by_sla: Optional[bool] = False


class CreateResume(BaseModel):
    vacancy_id: int
    source: ResumesSourceEnum
    current_stage: StageEnum
    sla_time: Optional[time]
    created_at: datetime
    updated_at: datetime

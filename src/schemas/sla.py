from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from src.schemas.enums import StageEnum
from src.schemas.user import UserDetail


class SLAUpdate(BaseModel):
    stage: StageEnum
    sla_duration: timedelta


class SLAUpdate(BaseModel):
    stage: StageEnum
    sla_duration: timedelta


class SLAViolation(BaseModel):
    resume_id: int
    stage: StageEnum
    time_exceeded: timedelta


class SLAViolationDetail(BaseModel):
    resume_id: int
    user: Optional[UserDetail]
    stage: str
    time_exceeded: str


class SLAResponse(BaseModel):
    violations: List[SLAViolation]


class SLAReportRequest(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    stage: Optional[StageEnum] = None
    user_id: Optional[int] = None


class SLAReportResponse(BaseModel):
    total_violations: int
    violations_detail: List[SLAViolationDetail]

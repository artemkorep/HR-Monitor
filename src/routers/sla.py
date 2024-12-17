from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from src.models.models import Resume, SLASettings, User, StageEnum
from src.schemas.schemas import SLAUpdate, SLAReportRequest, SLAReportResponse, SLAResponse
from src.core.db.database import session_local
from src.routers.dependencies import check_role
from src.models.models import UserRoleEnum
from src.core.db.database import get_db

router = APIRouter()

# 1. Проверить нарушения SLA
@router.get("/check_sla", response_model=SLAResponse, dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def check_sla(db: Session = Depends(get_db)):
    violations = []
    resumes = db.query(Resume).all()
    sla_settings = {sla.stage: sla.sla_duration for sla in db.query(SLASettings).all()}

    for resume in resumes:
        stage = resume.current_stage
        if stage in sla_settings:
            sla_duration = sla_settings[stage]
            time_on_stage = datetime.utcnow() - resume.updated_at
            if time_on_stage > sla_duration:
                violations.append({
                    "resume_id": resume.id_resume,
                    "stage": stage,
                    "time_exceeded": time_on_stage - sla_duration
                })

    return {"violations": violations}

# 2. Обновить настройки SLA
@router.post("/update_sla", dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def update_sla(sla: SLAUpdate, db: Session = Depends(get_db)):
    existing_sla = db.query(SLASettings).filter(SLASettings.stage == sla.stage).first()
    if existing_sla:
        existing_sla.sla_duration = sla.sla_duration
    else:
        new_sla = SLASettings(stage=sla.stage, sla_duration=sla.sla_duration)
        db.add(new_sla)
    db.commit()
    return {"message": "SLA updated successfully"}

# 3. Генерация отчета по SLA
@router.post("/sla_report", response_model=SLAReportResponse, dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def get_sla_report(filters: SLAReportRequest, db: Session = Depends(get_db)):
    sla_settings = {sla.stage: sla.sla_duration for sla in db.query(SLASettings).all()}

    # Базовый запрос
    query = db.query(Resume, User).join(User, Resume.user_id == User.id_user)

    # Применение фильтров
    if filters.from_date:
        query = query.filter(Resume.updated_at >= filters.from_date)

    if filters.to_date:
        query = query.filter(Resume.updated_at <= filters.to_date)

    if filters.stage:
        query = query.filter(Resume.current_stage == filters.stage)

    if filters.user_id:
        query = query.filter(Resume.user_id == filters.user_id)

    # Подготовка данных
    total_violations = 0
    violations_detail = []
    for resume, user in query.all():
        stage = resume.current_stage
        if stage in sla_settings:
            sla_duration = sla_settings[stage]
            time_on_stage = datetime.utcnow() - resume.updated_at
            if time_on_stage > sla_duration:
                total_violations += 1
                violations_detail.append({
                    "resume_id": resume.id_resume,
                    "user": f"{user.first_name} {user.last_name}",
                    "stage": stage,
                    "time_exceeded": time_on_stage - sla_duration
                })

    return {
        "total_violations": total_violations,
        "violations_detail": violations_detail
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.models.models import Resume, SLASettings, User, UserTeamLead
from src.schemas import (
    SLAUpdate,
    SLAReportRequest,
    SLAReportResponse,
    SLAResponse,
)
from src.core.dependencies import check_team_lead
from src.core.db.database import get_db

router = APIRouter()


@router.post("/activate_hr")
async def activate_hr(
    hr_id: int, db: Session = Depends(get_db), user: dict = Depends(check_team_lead)
):
    existing_team_lead = (
        db.query(UserTeamLead).filter(UserTeamLead.hr_user_id == hr_id).first()
    )
    if existing_team_lead:
        raise HTTPException(status_code=400, detail="This HR is already assigned")
    new_team_lead_assignment = UserTeamLead(team_lead_user_id=user.id, hr_user_id=hr_id)
    db.add(new_team_lead_assignment)
    db.commit()


@router.delete("/deactivate_hr")
async def deactivate_hr(
    hr_id: int, db: Session = Depends(get_db), user: dict = Depends(check_team_lead)
):
    existing_hr = (
        db.query(UserTeamLead)
        .filter(UserTeamLead.hr_user_id == hr_id)
        .filter(UserTeamLead.team_lead_user_id == user.id)
        .first()
    )
    if not (existing_hr):
        raise HTTPException(
            status_code=400,
            detail="HR has not been found, or you are not his team lead",
        )
    db.delete(existing_hr)
    db.commit()


@router.get(
    "/check",
    response_model=SLAResponse,
    dependencies=[Depends(check_team_lead)],
)
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
                user = db.query(User).filter(User.id == resume.user_id).first()
                violations.append(
                    {
                        "resume_id": resume.id,
                        "stage": stage,
                        "time_exceeded": str(time_on_stage - sla_duration),
                        "user": (
                            {
                                "id": user.id,
                                "name": user.first_name,
                                "email": user.email,
                            }
                            if user
                            else None
                        ),
                    }
                )

    return {"violations": violations}


@router.post("/update", dependencies=[Depends(check_team_lead)])
async def update_sla(sla: SLAUpdate, db: Session = Depends(get_db)) -> SLAUpdate:
    existing_sla = db.query(SLASettings).filter(SLASettings.stage == sla.stage).first()
    if existing_sla:
        existing_sla.sla_duration = sla.sla_duration
    else:
        new_sla = SLASettings(stage=sla.stage, sla_duration=sla.sla_duration)
        db.add(new_sla)
    db.commit()
    return sla


@router.post(
    "/report",
    dependencies=[Depends(check_team_lead)],
)
async def get_sla_report(
    filters: SLAReportRequest, db: Session = Depends(get_db)
) -> SLAReportResponse:
    sla_settings = {sla.stage: sla.sla_duration for sla in db.query(SLASettings).all()}

    query = db.query(Resume, User).join(User, Resume.user_id == User.id)

    if filters.from_date:
        query = query.filter(Resume.updated_at >= filters.from_date)

    if filters.to_date:
        query = query.filter(Resume.updated_at <= filters.to_date)

    if filters.stage:
        query = query.filter(Resume.current_stage == filters.stage)

    if filters.user_id:
        query = query.filter(Resume.user_id == filters.user_id)

    total_violations = 0
    violations_detail = []

    for resume, user in query.all():
        stage = resume.current_stage
        if stage in sla_settings:
            sla_duration = sla_settings[stage]
            time_on_stage = datetime.utcnow() - resume.updated_at
            if time_on_stage > sla_duration:
                total_violations += 1
                violations_detail.append(
                    {
                        "resume_id": resume.id,
                        "stage": stage,
                        "time_exceeded": str(time_on_stage - sla_duration),
                        "user": (
                            {
                                "id": user.id,
                                "name": user.first_name,
                                "email": user.email,
                            }
                            if user
                            else None
                        ),
                    }
                )

    return {
        "total_violations": total_violations,
        "violations_detail": violations_detail,
    }

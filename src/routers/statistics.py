from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.schemas import UserRoleEnum
from src.models.models import Resume, Vacancy, User, UserTeamLead
from src.core.dependencies import get_current_user
from src.core.db.database import get_db

router = APIRouter()


@router.get("/")
async def get_statistics(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    avg_time_per_stage = {}
    distribution_per_stage = {}
    distribution_per_source = {}
    sla_violations = 0

    if current_user.role == UserRoleEnum.hr:
        resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    elif current_user.role == UserRoleEnum.team_lead:

        hr_ids = (
            db.query(User.id)
            .join(UserTeamLead, UserTeamLead.team_lead_user_id == current_user.id)
            .all()
        )
        hr_ids = [hr_id[0] for hr_id in hr_ids]

        resumes = db.query(Resume).filter(Resume.user_id.in_(hr_ids)).all()
    else:

        resumes = db.query(Resume).all()

    for resume in resumes:
        sla_seconds = 0
        if resume.sla_time:
            sla_seconds = (
                resume.sla_time.hour * 3600
                + resume.sla_time.minute * 60
                + resume.sla_time.second
            )

        if resume.current_stage not in avg_time_per_stage:
            avg_time_per_stage[resume.current_stage] = []
        avg_time_per_stage[resume.current_stage].append(sla_seconds)

        if resume.current_stage not in distribution_per_stage:
            distribution_per_stage[resume.current_stage] = 0
        distribution_per_stage[resume.current_stage] += 1

        if resume.source not in distribution_per_source:
            distribution_per_source[resume.source] = 0
        distribution_per_source[resume.source] += 1

        if resume.sla_time and sla_seconds > (
            resume.sla_time.hour * 3600
            + resume.sla_time.minute * 60
            + resume.sla_time.second
        ):
            sla_violations += 1

    avg_time_per_stage_result = {
        stage: sum(times) / len(times) for stage, times in avg_time_per_stage.items()
    }

    if current_user.role == UserRoleEnum.hr:
        avg_candidates_per_vacancy = (
            db.query(Vacancy.id, func.count(Resume.id).label("candidates_count"))
            .join(Resume, Resume.vacancy_id == Vacancy.id)
            .filter(Resume.user_id == current_user.id)
            .group_by(Vacancy.id)
            .all()
        )
    elif current_user.role == UserRoleEnum.team_lead:
        avg_candidates_per_vacancy = (
            db.query(Vacancy.id, func.count(Resume.id).label("candidates_count"))
            .join(Resume, Resume.vacancy_id == Vacancy.id)
            .filter(Resume.user_id.in_(hr_ids))
            .group_by(Vacancy.id)
            .all()
        )

    avg_candidates_per_vacancy_result = [
        {"vacancy_id": row.id, "candidates_count": row.candidates_count}
        for row in avg_candidates_per_vacancy
    ]

    return {
        "avg_time_per_stage": avg_time_per_stage_result,
        "distribution_per_stage": distribution_per_stage,
        "distribution_per_source": distribution_per_source,
        "avg_candidates_per_vacancy": avg_candidates_per_vacancy_result,
        "sla_violations": sla_violations,
    }

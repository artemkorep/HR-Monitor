from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Resume, Vacancy
from src.core.db.database import session_local
from src.routers.dependencies import check_role
from src.models.models import UserRoleEnum
from src.core.db.database import get_db

router = APIRouter()


@router.get("/", dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def get_statistics(db: Session = Depends(get_db)):
    avg_time_per_stage = {}
    distribution_per_stage = {}
    distribution_per_source = {}
    sla_violations = 0

    resumes = db.query(Resume).all()

    for resume in resumes:
        sla_seconds = (
            resume.sla_time.hour * 3600
            + resume.sla_time.minute * 60
            + resume.sla_time.second
            if resume.sla_time
            else 0
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

    avg_candidates_per_vacancy = (
        db.query(
            Vacancy.id_vacancy, func.count(Resume.id_resume).label("candidates_count")
        )
        .join(Resume)
        .group_by(Vacancy.id_vacancy)
        .all()
    )

    avg_candidates_per_vacancy_result = [
        {"vacancy_id": row.id_vacancy, "candidates_count": row.candidates_count}
        for row in avg_candidates_per_vacancy
    ]

    return {
        "avg_time_per_stage": avg_time_per_stage_result,
        "distribution_per_stage": distribution_per_stage,
        "distribution_per_source": distribution_per_source,
        "avg_candidates_per_vacancy": avg_candidates_per_vacancy_result,
        "sla_violations": sla_violations,
    }

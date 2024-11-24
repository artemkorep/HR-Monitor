from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Resume, Vacancy
from src.core.db.database import session_local
from src.routers.dependencies import check_role
from src.models.models import UserRoleEnum

router = APIRouter()

# Зависимость для получения сессии базы данных
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Получение статистики (только для HR Team Lead)
@router.get("/", dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def get_statistics(db: Session = Depends(get_db)):
    avg_time_per_stage = {}
    distribution_per_stage = {}
    distribution_per_source = {}
    sla_violations = 0

    resumes = db.query(Resume).all()

    for resume in resumes:
        if resume.current_stage not in avg_time_per_stage:
            avg_time_per_stage[resume.current_stage] = []
        avg_time_per_stage[resume.current_stage].append(resume.sla_time)

        if resume.current_stage not in distribution_per_stage:
            distribution_per_stage[resume.current_stage] = 0
        distribution_per_stage[resume.current_stage] += 1

        if resume.source not in distribution_per_source:
            distribution_per_source[resume.source] = 0
        distribution_per_source[resume.source] += 1

        if resume.sla_time and resume.sla_time > resume.sla_time:
            sla_violations += 1

    avg_candidates_per_vacancy = db.query(Vacancy, func.count(Resume.id_resume).label("candidates_count")) \
        .join(Resume).group_by(Vacancy.id_vacancy).all()

    return {
        "avg_time_per_stage": {stage: sum(times) / len(times) for stage, times in avg_time_per_stage.items()},
        "distribution_per_stage": distribution_per_stage,
        "distribution_per_source": distribution_per_source,
        "avg_candidates_per_vacancy": avg_candidates_per_vacancy,
        "sla_violations": sla_violations
    }

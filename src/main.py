from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.models import Base, Resume, Vacancy, User
from src.schemas.schemas import ResumeFilter, StageEnum, ResumesSourceEnum
from src.core.db.database import engine, session_local


app = FastAPI(
    title="HR Monitor",
    description="API для мониторинга эффективности работы рекрутеров.",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


def getdb():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


# Получить статистику в реальном времени
@app.get("/statistics")
async def get_statistics(db: Session = Depends(getdb)):
    # Сбор статистики по стадиям
    avg_time_per_stage = {}
    distribution_per_stage = {}
    distribution_per_source = {}
    sla_violations = 0

    # Считаем среднее время нахождения в стадии
    resumes = db.query(Resume).all()

    for resume in resumes:
        # Логика для подсчета среднего времени на стадии
        if resume.current_stage not in avg_time_per_stage:
            avg_time_per_stage[resume.current_stage] = []
        avg_time_per_stage[resume.current_stage].append(resume.sla_time)

        if resume.current_stage not in distribution_per_stage:
            distribution_per_stage[resume.current_stage] = 0
        distribution_per_stage[resume.current_stage] += 1

        if resume.source not in distribution_per_source:
            distribution_per_source[resume.source] = 0
        distribution_per_source[resume.source] += 1

        # SLA нарушения (например, если время на стадии больше SLA)
        if resume.sla_time and resume.sla_time > resume.sla_time:
            sla_violations += 1

    # Вычисление среднего количества кандидатов на вакансию
    avg_candidates_per_vacancy = db.query(Vacancy, func.count(Resume.id_resume).label("candidates_count")) \
        .join(Resume).group_by(Vacancy.id_vacancy).all()

    return {
        "avg_time_per_stage": {stage: sum(times) / len(times) for stage, times in avg_time_per_stage.items()},
        "distribution_per_stage": distribution_per_stage,
        "distribution_per_source": distribution_per_source,
        "avg_candidates_per_vacancy": avg_candidates_per_vacancy,
        "sla_violations": sla_violations
    }


# Фильтрация резюме
@app.post("/filter_resumes")
async def filter_resumes(filters: ResumeFilter, db: Session = Depends(getdb)):
    query = db.query(Resume)

    if filters.stage:
        query = query.filter(Resume.current_stage == filters.stage)

    if filters.vacancy_id:
        query = query.filter(Resume.vacancy_id == filters.vacancy_id)

    if filters.from_date:
        query = query.filter(Resume.created_at >= filters.from_date)

    if filters.to_date:
        query = query.filter(Resume.created_at <= filters.to_date)

    if filters.from_sla:
        query = query.filter(Resume.sla_time >= filters.from_sla)

    if filters.to_sla:
        query = query.filter(Resume.sla_time <= filters.to_sla)

    if filters.sort_by_date:
        query = query.order_by(Resume.created_at.desc())

    if filters.sort_by_sla:
        query = query.order_by(Resume.sla_time)

    return query.all()


# Обновить стадию резюме
@app.patch("/update_resume_stage/{resume_id}")
async def update_resume_stage(resume_id: int, new_stage: str, db: Session = Depends(getdb)):
    resume = db.query(Resume).filter(Resume.id_resume == resume_id).first()
    if resume:
        resume.current_stage = new_stage
        db.commit()
        return {"message": "Resume stage updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Resume not found")
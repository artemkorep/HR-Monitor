from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.models.models import Resume
from src.schemas import ResumeFilter, CreateResume
from src.core.dependencies import check_hr, get_current_user
from src.models.models import Resume, Vacancy
from src.core.db.database import get_db


router = APIRouter()


@router.post("/create")
async def create_resume(
    resume: CreateResume,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CreateResume:
    vacancy = db.query(Vacancy).filter_by(id=resume.vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    new_resume = Resume(
        user_id=current_user.id,
        vacancy_id=resume.vacancy_id,
        source=resume.source,
        current_stage=resume.current_stage,
        sla_time=resume.sla_time,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return CreateResume(
        user_id=new_resume.user_id,
        vacancy_id=new_resume.vacancy_id,
        source=new_resume.source,
        current_stage=new_resume.current_stage,
        sla_time=new_resume.sla_time,
        created_at=new_resume.created_at,
        updated_at=new_resume.updated_at,
    )


@router.post("/filter", dependencies=[Depends(check_hr)])
async def filter_resumes(filters: ResumeFilter, db: Session = Depends(get_db)):
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


@router.patch("/update_stage/{resume_id}", dependencies=[Depends(check_hr)])
async def update_resume_stage(
    resume_id: int, new_stage: str, db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume:
        resume.current_stage = new_stage
        db.commit()
        return {"message": "Resume stage updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Resume not found")

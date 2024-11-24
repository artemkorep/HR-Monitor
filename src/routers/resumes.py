from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.models.models import Resume
from src.schemas.schemas import ResumeFilter
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

# Фильтрация резюме (только для HR)
@router.post("/filter", dependencies=[Depends(check_role(UserRoleEnum.hr))])
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

# Обновление стадии резюме (только для HR)
@router.patch("/update_stage/{resume_id}", dependencies=[Depends(check_role(UserRoleEnum.hr))])
async def update_resume_stage(resume_id: int, new_stage: str, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id_resume == resume_id).first()
    if resume:
        resume.current_stage = new_stage
        db.commit()
        return {"message": "Resume stage updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Resume not found")

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.models import Vacancy
from src.schemas.schemas import VacancyCreate
from src.core.db.database import session_local
from src.routers.dependencies import check_role
from src.models.models import UserRoleEnum
from src.core.db.database import get_db

router = APIRouter()


# Создание новой вакансии (только для Team Lead)
@router.post("/", dependencies=[Depends(check_role(UserRoleEnum.team_lead))])
async def create_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    new_vacancy = Vacancy(title=vacancy.title, description=vacancy.description)
    db.add(new_vacancy)
    db.commit()
    db.refresh(new_vacancy)
    return new_vacancy

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models.models import Vacancy
from src.schemas import VacancyCreate
from src.core.dependencies import check_team_lead
from src.core.db.database import get_db

router = APIRouter()


@router.post("/create", dependencies=[Depends(check_team_lead)])
async def create_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    new_vacancy = Vacancy(title=vacancy.title, description=vacancy.description)
    db.add(new_vacancy)
    db.commit()
    db.refresh(new_vacancy)
    return new_vacancy

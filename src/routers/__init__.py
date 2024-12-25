from fastapi import APIRouter
from .auth import router as auth
from .resumes import router as resumes
from .team_lead import router as team_lead
from .statistics import router as statistics
from .vacancies import router as vacancies


router = APIRouter(prefix="/api")
router.include_router(auth, prefix="/auth", tags=["Authorization"])
router.include_router(statistics, prefix="/statistics", tags=["Statistics"])
router.include_router(resumes, prefix="/resumes", tags=["Resumes"])
router.include_router(vacancies, prefix="/vacancies", tags=["Vacancies"])
router.include_router(team_lead, prefix="/team_lead", tags=["Team Lead"])

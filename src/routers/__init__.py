from fastapi import APIRouter
from .auth import router as auth
from .resumes import router as resumes
from .sla import router as sla
from .statistics import router as statistics
from .vacancies import router as vacancies
from .supervisor import router as supervisor


router = APIRouter(prefix="/api")
router.include_router(auth, prefix="/auth", tags=["Authorization"])
router.include_router(statistics, prefix="/statistics", tags=["Statistics"])
router.include_router(resumes, prefix="/resumes", tags=["Resumes"])
router.include_router(vacancies, prefix="/vacancies", tags=["Vacancies"])
router.include_router(sla, prefix="/sla", tags=["SLA"])
router.include_router(supervisor, prefix="/supervisor", tags=["Supervisor"])

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.models.models import User
from src.core.dependencies import check_admin
from src.core.db.database import get_db
from src.schemas import UserRoleEnum

router = APIRouter()


@router.get("/set_role", dependencies=[Depends(check_admin)])
async def set_user_role(
    user_id: int, role: UserRoleEnum, db: Session = Depends(get_db)
) -> None:

    user = db.query(User).filter(User.id_user == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.role = role
    db.commit()
    db.refresh(user)
    return {"message": f"User role changed to {role.value}"}

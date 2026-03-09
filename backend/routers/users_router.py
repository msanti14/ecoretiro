from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import get_db, get_current_user
from backend.models.user_model import User
from backend.schemas.user_schema import UserRead, UserUpdate
from backend.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserRead:
    return user_service.get_me(db, current_user.id)

@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserRead:
    return user_service.update_me(db, current_user.id, data)
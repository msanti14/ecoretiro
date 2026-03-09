from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import get_db
from backend.core.security import create_access_token
from backend.schemas.user_schema import UserCreate, UserRead, UserLogin
from backend.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    data: UserCreate,
    db: Session = Depends(get_db)
) -> UserRead:
    # Registra un nuevo usuario y retorna sus datos
    return user_service.create_user(db, data)

@router.post("/login")
async def login(
    data: UserLogin,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Autentica al usuario y retorna el JWT
    user = user_service.authenticate_user(db, data.email, data.password)
    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}
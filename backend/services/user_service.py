from sqlalchemy.orm import Session
from backend.models.user_model import User
from backend.schemas.user_schema import UserCreate
from backend.repositories import user_repository
from backend.core.security import verify_password
from backend.core.exceptions import EcoRetiroExceptions

def create_user(db: Session, data: UserCreate) -> User:
    # Verifica que el email no esté registrado antes de crear
    existing = user_repository.get_by_email(db, data.email)
    if existing:
        raise EcoRetiroExceptions.EMAIL_ALREADY_EXISTS
    return user_repository.create(db, data)

def authenticate_user(db: Session, email: str, password: str) -> User:
    # Verifica credenciales y retorna el usuario si son válidas
    user = user_repository.get_by_email(db, email)
    if not user:
        raise EcoRetiroExceptions.INVALID_CREDENTIALS
    if not verify_password(password, user.password_hash):
        raise EcoRetiroExceptions.INVALID_CREDENTIALS
    return user

def get_user_or_404(db: Session, user_id: str) -> User:
    # Retorna el usuario o lanza 404 si no existe
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise EcoRetiroExceptions.USER_NOT_FOUND
    return user
from sqlalchemy.orm import Session
from uuid import UUID
from backend.models.user_model import User
from backend.schemas.user_schema import UserCreate, UserUpdate
from backend.repositories import user_repository
from backend.core.security import verify_password, hash_password
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

def get_me(db: Session, user_id: UUID) -> User:
    # Retorna el perfil del usuario autenticado o lanza 404
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise EcoRetiroExceptions.USER_NOT_FOUND
    return user

def update_me(db: Session, user_id: UUID, data: UserUpdate) -> User:
    # Actualiza el perfil del usuario actual
    # Maneja la validación y hasheado de contraseña
    user = get_me(db, user_id)
    
    # Si se proporciona nueva contraseña, validar actual
    if data.password:
        if not verify_password(data.current_password, user.password_hash):
            raise EcoRetiroExceptions.INVALID_CREDENTIALS
    
    # Actualizar campos no-contraseña primero
    updated_user = user_repository.update_user(db, user_id, data)
    if not updated_user:
        raise EcoRetiroExceptions.USER_NOT_FOUND
    
    # Si hay nueva contraseña, actualizarla por separado
    if data.password:
        updated_user.password_hash = hash_password(data.password)
        db.commit()
        db.refresh(updated_user)
    
    return updated_user
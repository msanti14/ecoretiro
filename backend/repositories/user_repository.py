from sqlalchemy.orm import Session
from uuid import UUID
from backend.models.user_model import User
from backend.schemas.user_schema import UserCreate, UserUpdate
from backend.core.security import hash_password

def get_by_id(db: Session, user_id: UUID) -> User | None:
    # Busca usuario por ID
    return db.query(User).filter(User.id == user_id).first()

def get_by_email(db: Session, email: str) -> User | None:
    # Busca usuario por email
    return db.query(User).filter(User.email == email).first()

def create(db: Session, data: UserCreate) -> User:
    # Crea un nuevo usuario hasheando la contraseña
    try:
        new_user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            phone=data.phone
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception:
        db.rollback()
        raise

def update_user(db: Session, user_id: UUID, data: UserUpdate) -> User | None:
    try:
        user = get_by_id(db, user_id)
        if not user:
            return None
        update_data = data.model_dump(exclude_unset=True, exclude={"password", "current_password"})
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise
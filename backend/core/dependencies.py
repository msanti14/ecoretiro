from typing import Generator
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.core.security import decode_access_token
from backend.core.exceptions import EcoRetiroExceptions

def get_db() -> Generator[Session, None, None]:
    # Abre una sesión de DB y la cierra al terminar la request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(authorization: str = Header(...)) -> str:
    # Extrae y valida el JWT del header Authorization
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise EcoRetiroExceptions.INVALID_CREDENTIALS
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise EcoRetiroExceptions.INVALID_CREDENTIALS
        return user_id
    except ValueError:
        raise EcoRetiroExceptions.INVALID_CREDENTIALS
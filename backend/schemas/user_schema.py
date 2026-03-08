from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from backend.models.user_model import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None

    @field_validator("name")
    @classmethod
    def name_length(cls, v: str) -> str:
        # Mínimo 2 caracteres, máximo 100
        if len(v.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        # Mínimo 8 caracteres y al menos un número
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        # Solo dígitos, entre 7 y 15 caracteres
        if v is not None:
            if not v.isdigit() or not (7 <= len(v) <= 15):
                raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return v

class UserRead(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    phone: str | None = None
    created_at: datetime
    # password_hash ausente siempre
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str
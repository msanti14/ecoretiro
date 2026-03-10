import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from backend.database import Base

class UserRole(str, enum.Enum):
    USER = "USER"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.USER, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # Relaciones
    requests: Mapped[list["Request"]] = relationship(
        "Request", foreign_keys="Request.user_id", back_populates="user"
    )
    operated_requests: Mapped[list["Request"]] = relationship(
        "Request", foreign_keys="Request.operator_id", back_populates="operator"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user"
    )
    status_histories: Mapped[list["StatusHistory"]] = relationship(
        "StatusHistory", back_populates="user"
    )
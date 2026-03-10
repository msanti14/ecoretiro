"""
Modelo Notification: notificaciones internas almacenadas en BD.
Se relacionan con User (required) y Request (opcional).
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    request_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("requests.id"), nullable=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relaciones
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    request: Mapped["Request | None"] = relationship("Request", foreign_keys=[request_id], back_populates="notifications")

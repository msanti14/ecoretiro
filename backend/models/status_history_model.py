"""
Modelo StatusHistory: historial de estados de una solicitud.
Requerido por request_repository.create_with_history (transacción atómica).
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.request_model import RequestStatus


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requests.id"), nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus), nullable=False
    )
    updated_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relaciones
    request: Mapped["Request"] = relationship("Request", foreign_keys=[request_id], back_populates="status_histories")
    user: Mapped["User"] = relationship("User", foreign_keys=[updated_by], back_populates="status_histories")

"""
Modelo StatusHistory: historial de estados de una solicitud.
Requerido por request_repository.create_with_history (transacción atómica).
"""
import uuid
from datetime import datetime
from sqlalchemy import Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
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
        default=datetime.utcnow, nullable=False
    )

"""
Modelo Request: solicitud de retiro de residuos electrónicos.
Campos, enums y relaciones según ARCHITECTURE.md.
"""
import uuid
import enum
from datetime import datetime, date, timezone
from sqlalchemy import String, Text, Float, Date, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class MaterialType(str, enum.Enum):
    COMPUTADORA = "COMPUTADORA"
    MONITOR = "MONITOR"
    TELEVISOR = "TELEVISOR"
    IMPRESORA = "IMPRESORA"
    CELULAR = "CELULAR"
    TABLET = "TABLET"
    ELECTRODOMESTICO = "ELECTRODOMESTICO"
    CABLE = "CABLE"
    PLACA_CIRCUITO = "PLACA_CIRCUITO"
    PILA_BATERIA = "PILA_BATERIA"
    OTRO = "OTRO"


class EstimatedVolume(str, enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


class PickupTimeRange(str, enum.Enum):
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"


class RequestStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    SCHEDULED = "SCHEDULED"
    IN_ROUTE = "IN_ROUTE"
    COLLECTED = "COLLECTED"
    CLASSIFIED = "CLASSIFIED"
    RECOVERED = "RECOVERED"
    SENT_TO_RECYCLING = "SENT_TO_RECYCLING"
    COMPLETED = "COMPLETED"


class VehicleAssigned(str, enum.Enum):
    DUCATO = "DUCATO"
    AUTO = "AUTO"


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    tracking_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    material_type: Mapped[MaterialType] = mapped_column(
        SAEnum(MaterialType), nullable=False
    )
    estimated_volume: Mapped[EstimatedVolume] = mapped_column(
        SAEnum(EstimatedVolume), nullable=False
    )
    pickup_date: Mapped[date] = mapped_column(Date, nullable=False)
    pickup_time_range: Mapped[PickupTimeRange] = mapped_column(
        SAEnum(PickupTimeRange), nullable=False
    )
    current_status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus), default=RequestStatus.REQUESTED, nullable=False
    )
    vehicle_assigned: Mapped[VehicleAssigned | None] = mapped_column(
        SAEnum(VehicleAssigned), nullable=True
    )
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones: usuario que creó la solicitud y operador asignado (si hay).
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="requests"
    )
    operator: Mapped["User | None"] = relationship(
        "User", foreign_keys=[operator_id], back_populates="operated_requests"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="request"
    )
    status_histories: Mapped[list["StatusHistory"]] = relationship(
        "StatusHistory", back_populates="request"
    )

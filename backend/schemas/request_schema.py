"""
Schemas de Request: validación de entrada/salida para solicitudes de retiro.
RequestCreate, RequestRead, RequestUpdate y TrackingResponse según ARCHITECTURE.md.
"""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from backend.models.request_model import (
    EstimatedVolume,
    MaterialType,
    PickupTimeRange,
    RequestStatus,
    VehicleAssigned,
)


# --- RequestCreate: body de POST /requests ---

class RequestCreate(BaseModel):
    address: str
    lat: float | None = None
    lng: float | None = None
    description: str
    material_type: MaterialType
    estimated_volume: EstimatedVolume
    pickup_date: date
    pickup_time_range: PickupTimeRange

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("La descripción debe tener al menos 10 caracteres")
        if len(v) > 500:
            raise ValueError("La descripción no puede superar 500 caracteres")
        return v.strip()

    @field_validator("pickup_date")
    @classmethod
    def pickup_date_not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("La fecha de retiro no puede ser pasada")
        return v

    @field_validator("lat")
    @classmethod
    def lat_range(cls, v: float | None) -> float | None:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        return v

    @field_validator("lng")
    @classmethod
    def lng_range(cls, v: float | None) -> float | None:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180")
        return v


# --- RequestRead: respuesta de GET /requests/{id} y /requests/me ---

class RequestRead(BaseModel):
    id: UUID
    tracking_number: str
    user_id: UUID
    address: str
    lat: float | None
    lng: float | None
    description: str
    material_type: MaterialType
    estimated_volume: EstimatedVolume
    pickup_date: date
    pickup_time_range: PickupTimeRange
    current_status: RequestStatus
    vehicle_assigned: VehicleAssigned | None
    operator_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- RequestUpdate: body de PATCH /requests/{id}/status (operador) ---

class RequestUpdate(BaseModel):
    current_status: RequestStatus | None = None
    vehicle_assigned: VehicleAssigned | None = None
    operator_id: UUID | None = None


# --- TrackingResponse: respuesta pública de GET /track/{tracking_number} ---

class StatusHistoryItem(BaseModel):
    """Elemento del historial de estados para TrackingResponse."""
    status: RequestStatus
    timestamp: datetime


class TrackingResponse(BaseModel):
    tracking_number: str
    current_status: RequestStatus
    material_type: MaterialType
    pickup_date: date
    pickup_time_range: PickupTimeRange
    vehicle_assigned: VehicleAssigned | None
    history: list[StatusHistoryItem]

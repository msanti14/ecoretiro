"""
Servicio de Request: lógica de negocio de solicitudes de retiro.
Delega en request_repository; valida transiciones con tracking_service.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.request_model import Request
from backend.schemas.request_schema import (
    RequestCreate,
    RequestUpdate,
    TrackingResponse,
    StatusHistoryItem,
)
from backend.repositories import request_repository
from backend.services.tracking_service import validate_transition
from backend.core.exceptions import EcoRetiroExceptions


def create_request(
    db: Session, data: RequestCreate, user_id: UUID
) -> Request:
    """Crea una solicitud (transacción atómica: request + history + vehículo)."""
    return request_repository.create_with_history(db, data, user_id)


def get_request_or_404(db: Session, request_id: UUID) -> Request:
    """Retorna la solicitud por ID o lanza 404."""
    request = request_repository.get_by_id(db, request_id)
    if not request:
        raise EcoRetiroExceptions.REQUEST_NOT_FOUND
    return request


def get_my_requests(db: Session, user_id: UUID) -> list[Request]:
    """Lista las solicitudes del usuario."""
    return request_repository.get_by_user(db, user_id)


def get_all_requests(db: Session) -> list[Request]:
    """Lista todas las solicitudes (uso OPERATOR/ADMIN)."""
    return request_repository.get_all(db)


def get_tracking_response(db: Session, tracking_number: str) -> TrackingResponse:
    """Respuesta pública de seguimiento por tracking_number. Lanza 404 si no existe."""
    request = request_repository.get_by_tracking_number(db, tracking_number)
    if not request:
        raise EcoRetiroExceptions.REQUEST_NOT_FOUND
    history = request_repository.get_history_by_request_id(db, request.id)
    return TrackingResponse(
        tracking_number=request.tracking_number,
        current_status=request.current_status,
        material_type=request.material_type,
        pickup_date=request.pickup_date,
        pickup_time_range=request.pickup_time_range,
        vehicle_assigned=request.vehicle_assigned,
        history=[
            StatusHistoryItem(status=h.status, timestamp=h.timestamp)
            for h in history
        ],
    )


def update_status(
    db: Session,
    request_id: UUID,
    data: RequestUpdate,
    operator_id: UUID,
) -> Request:
    """
    Actualiza estado (y opcionalmente vehicle_assigned, operator_id).
    Valida transición con ALLOWED_TRANSITIONS; transacción atómica
    (actualiza request + inserta StatusHistory).
    """
    request = get_request_or_404(db, request_id)
    if data.current_status is not None:
        validate_transition(request.current_status, data.current_status)
        updated = request_repository.update_status_with_history(
            db,
            request_id,
            data.current_status,
            operator_id,
            notes=None,
            vehicle_assigned=data.vehicle_assigned,
            operator_id_assign=data.operator_id,
        )
        if not updated:
            raise EcoRetiroExceptions.REQUEST_NOT_FOUND
        return updated
    # Solo actualización de vehicle_assigned u operator_id (sin cambio de estado)
    if data.vehicle_assigned is not None:
        request.vehicle_assigned = data.vehicle_assigned
    if data.operator_id is not None:
        request.operator_id = data.operator_id
    if data.vehicle_assigned is not None or data.operator_id is not None:
        db.commit()
        db.refresh(request)
    return request

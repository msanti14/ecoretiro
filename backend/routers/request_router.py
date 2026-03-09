"""
Router de Request: endpoints HTTP para solicitudes de retiro.
Solo HTTP y delegación a request_service; auth vía core/dependencies.
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import (
    get_db,
    get_current_user_id,
    get_current_user_info,
    require_operator_or_admin,
)
from backend.core.exceptions import EcoRetiroExceptions
from backend.schemas.request_schema import (
    RequestCreate,
    RequestRead,
    RequestUpdate,
    TrackingResponse,
)
from backend.services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestRead, status_code=201)
def create_request(
    data: RequestCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> RequestRead:
    """Crea una solicitud de retiro (auth: cualquier usuario)."""
    return request_service.create_request(db, data, UUID(user_id))


@router.get("/me", response_model=list[RequestRead])
def list_my_requests(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> list[RequestRead]:
    """Lista las solicitudes del usuario autenticado."""
    return request_service.get_my_requests(db, UUID(user_id))


@router.get("", response_model=list[RequestRead])
def list_all_requests(
    db: Session = Depends(get_db),
    _operator_id: str = Depends(require_operator_or_admin),
) -> list[RequestRead]:
    """Lista todas las solicitudes. Auth: OPERATOR o ADMIN."""
    return request_service.get_all_requests(db)


@router.get("/{request_id}", response_model=RequestRead)
def get_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    user_info: dict[str, str] = Depends(get_current_user_info),
) -> RequestRead:
    """Obtiene una solicitud por ID. USER solo puede ver las propias."""
    request = request_service.get_request_or_404(db, request_id)
    if user_info["role"] == "USER" and str(request.user_id) != user_info["user_id"]:
        raise EcoRetiroExceptions.NOT_ENOUGH_PERMISSIONS
    return request


@router.patch("/{request_id}/status", response_model=RequestRead)
def update_request_status(
    request_id: UUID,
    data: RequestUpdate,
    db: Session = Depends(get_db),
    operator_id: str = Depends(require_operator_or_admin),
) -> RequestRead:
    """Actualiza estado (y opcionalmente vehículo/operador). Auth: OPERATOR o ADMIN."""
    return request_service.update_status(db, request_id, data, UUID(operator_id))


# Ruta pública de seguimiento (sin prefijo /requests para coincidir con ARCHITECTURE)
track_router = APIRouter(tags=["tracking"])


@track_router.get("/track/{tracking_number}", response_model=TrackingResponse)
def get_tracking(
    tracking_number: str,
    db: Session = Depends(get_db),
) -> TrackingResponse:
    """Consulta pública de seguimiento por número. Sin auth."""
    return request_service.get_tracking_response(db, tracking_number)

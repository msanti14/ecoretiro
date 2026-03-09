"""
Lógica de transiciones de estado de solicitudes.
ALLOWED_TRANSITIONS según ARCHITECTURE.md; validación unidireccional.
"""
from backend.models.request_model import RequestStatus
from backend.core.exceptions import EcoRetiroExceptions


ALLOWED_TRANSITIONS: dict[RequestStatus, list[RequestStatus]] = {
    RequestStatus.REQUESTED: [RequestStatus.SCHEDULED],
    RequestStatus.SCHEDULED: [RequestStatus.IN_ROUTE],
    RequestStatus.IN_ROUTE: [RequestStatus.COLLECTED],
    RequestStatus.COLLECTED: [RequestStatus.CLASSIFIED],
    RequestStatus.CLASSIFIED: [
        RequestStatus.RECOVERED,
        RequestStatus.SENT_TO_RECYCLING,
    ],
    RequestStatus.RECOVERED: [RequestStatus.COMPLETED],
    RequestStatus.SENT_TO_RECYCLING: [RequestStatus.COMPLETED],
    RequestStatus.COMPLETED: [],
}


def validate_transition(
    current_status: RequestStatus, new_status: RequestStatus
) -> None:
    """
    Valida que la transición de current_status a new_status esté permitida.
    Lanza EcoRetiroExceptions.INVALID_STATUS_TRANSITION si no es válida.
    """
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise EcoRetiroExceptions.INVALID_STATUS_TRANSITION

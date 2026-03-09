"""
Repositorio de Request: todas las consultas y escrituras a DB de solicitudes.
create_with_history es atómico: request + StatusHistory REQUESTED + asignación de vehículo.
"""
from datetime import date
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.models.request_model import (
    Request,
    RequestStatus,
    VehicleAssigned,
    EstimatedVolume,
)
from backend.models.status_history_model import StatusHistory
from backend.schemas.request_schema import RequestCreate


def get_by_id(db: Session, request_id: UUID) -> Request | None:
    """Busca una solicitud por ID."""
    return db.get(Request, request_id)


def get_by_tracking_number(db: Session, tracking_number: str) -> Request | None:
    """Busca una solicitud por tracking_number. Retorna None si no existe."""
    stmt = select(Request).where(Request.tracking_number == tracking_number)
    return db.execute(stmt).scalar_one_or_none()


def get_by_user(db: Session, user_id: UUID) -> list[Request]:
    """Lista todas las solicitudes del usuario, ordenadas por created_at descendente."""
    stmt = (
        select(Request)
        .where(Request.user_id == user_id)
        .order_by(Request.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_history_by_request_id(db: Session, request_id: UUID) -> list[StatusHistory]:
    """Historial de estados de una solicitud, ordenado por timestamp ascendente."""
    stmt = (
        select(StatusHistory)
        .where(StatusHistory.request_id == request_id)
        .order_by(StatusHistory.timestamp.asc())
    )
    return list(db.execute(stmt).scalars().all())


def get_all(db: Session) -> list[Request]:
    """Lista todas las solicitudes (para OPERATOR/ADMIN), ordenadas por created_at descendente."""
    stmt = select(Request).order_by(Request.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def _assign_vehicle(estimated_volume: EstimatedVolume) -> VehicleAssigned:
    """Asignación automática según ARCHITECTURE: SMALL/MEDIUM → AUTO, LARGE → DUCATO."""
    if estimated_volume == EstimatedVolume.LARGE:
        return VehicleAssigned.DUCATO
    return VehicleAssigned.AUTO


def generate_tracking_number(db: Session) -> str:
    """
    Genera el siguiente tracking_number del año.
    Formato: ECO-USHUAIA-{AÑO}-{SECUENCIA_5_DIGITOS}.
    Secuencia anual; debe llamarse dentro de la transacción de creación.
    """
    current_year = date.today().year
    prefix = f"ECO-USHUAIA-{current_year}-"
    # Contar solicitudes ya creadas en el año (por prefijo del tracking_number)
    subq = select(func.count()).select_from(Request).where(
        Request.tracking_number.like(f"{prefix}%")
    )
    count = db.execute(subq).scalar()
    sequence = (count or 0) + 1
    return f"{prefix}{str(sequence).zfill(5)}"


def create_with_history(
    db: Session, data: RequestCreate, user_id: UUID
) -> Request:
    """
    Transacción atómica: crea la solicitud, inserta REQUESTED en StatusHistory
    y asigna el vehículo según estimated_volume.
    """
    try:
        tracking_number = generate_tracking_number(db)
        vehicle = _assign_vehicle(data.estimated_volume)

        new_request = Request(
            tracking_number=tracking_number,
            user_id=user_id,
            address=data.address,
            lat=data.lat,
            lng=data.lng,
            description=data.description,
            material_type=data.material_type,
            estimated_volume=data.estimated_volume,
            pickup_date=data.pickup_date,
            pickup_time_range=data.pickup_time_range,
            vehicle_assigned=vehicle,
        )
        db.add(new_request)
        db.flush()

        history_entry = StatusHistory(
            request_id=new_request.id,
            status=RequestStatus.REQUESTED,
            updated_by=user_id,
        )
        db.add(history_entry)
        db.commit()
        db.refresh(new_request)
        return new_request
    except Exception:
        db.rollback()
        raise


def update_status_with_history(
    db: Session,
    request_id: UUID,
    new_status: RequestStatus,
    operator_id: UUID,
    notes: str | None = None,
    vehicle_assigned: VehicleAssigned | None = None,
    operator_id_assign: UUID | None = None,
) -> Request | None:
    """
    Transacción atómica: actualiza current_status en Request (y opcionalmente
    vehicle_assigned, operator_id), e inserta el nuevo estado en StatusHistory.
    """
    try:
        request = db.get(Request, request_id)
        if not request:
            return None
        request.current_status = new_status
        if vehicle_assigned is not None:
            request.vehicle_assigned = vehicle_assigned
        if operator_id_assign is not None:
            request.operator_id = operator_id_assign
        db.flush()
        history_entry = StatusHistory(
            request_id=request_id,
            status=new_status,
            updated_by=operator_id,
            notes=notes,
        )
        db.add(history_entry)
        db.commit()
        db.refresh(request)
        return request
    except Exception:
        db.rollback()
        raise

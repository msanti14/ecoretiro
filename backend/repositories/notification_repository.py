"""
Repositorio de Notification: consultas y escrituras a DB de notificaciones.
Sin lógica de negocio — solo acceso a BD.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.notification_model import Notification


def get_by_id(db: Session, notification_id: UUID) -> Notification | None:
    """Busca una notificación por ID."""
    return db.get(Notification, notification_id)


def get_by_user(db: Session, user_id: UUID) -> list[Notification]:
    """
    Lista todas las notificaciones del usuario, ordenadas por created_at descendente.
    Las más recientes primero.
    """
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def mark_as_read(db: Session, notification_id: UUID, user_id: UUID) -> Notification | None:
    """
    Marca una notificación como leída, solo si pertenece al usuario.
    Retorna la notificación actualizada o None si no existe/no pertenece.
    """
    try:
        notification = db.get(Notification, notification_id)
        if not notification or notification.user_id != user_id:
            return None
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise


def create(
    db: Session,
    user_id: UUID,
    message: str,
    request_id: UUID | None = None,
) -> Notification:
    """
    Crea una nueva notificación.
    request_id es opcional — no todas las notificaciones están ligadas a una solicitud.
    """
    try:
        new_notification = Notification(
            user_id=user_id,
            request_id=request_id,
            message=message,
            is_read=False,
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        return new_notification
    except Exception:
        db.rollback()
        raise

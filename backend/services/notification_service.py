"""
Servicio de Notification: lógica de negocio de notificaciones internas.
Delega en notification_repository; valida permisos y lanza excepciones.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.notification_model import Notification
from backend.models.user_model import User
from backend.repositories import notification_repository
from backend.core.exceptions import EcoRetiroExceptions


def get_my_notifications(db: Session, current_user: User) -> list[Notification]:
    """
    Retorna todas las notificaciones del usuario actual.
    Ordenadas por created_at descendente (más recientes primero).
    """
    return notification_repository.get_by_user(db, current_user.id)


def mark_notification_read(
    db: Session, notification_id: UUID, current_user: User
) -> Notification:
    """
    Marca una notificación como leída.
    Lanza 404 si no existe o no pertenece al usuario actual.
    """
    notification = notification_repository.mark_as_read(
        db, notification_id, current_user.id
    )
    if not notification:
        raise EcoRetiroExceptions.NOTIFICATION_NOT_FOUND
    return notification
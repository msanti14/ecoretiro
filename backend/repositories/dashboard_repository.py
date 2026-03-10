"""
Repositorio de Dashboard: queries de agregación para estadísticas de admin.
Sin lógica de negocio — solo acceso a DB con SQLAlchemy 2.0.
"""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.models.request_model import Request
from backend.models.user_model import User
from backend.models.notification_model import Notification


def get_stats(db: Session) -> dict:
    """
    Estadísticas del sistema para dashboard de admin.
    Retorna dict con totales y agregaciones.
    """
    # Total de solicitudes
    total_requests_stmt = select(func.count()).select_from(Request)
    total_requests = db.execute(total_requests_stmt).scalar() or 0

    # Solicitudes por estado
    requests_by_status_stmt = (
        select(Request.current_status, func.count())
        .group_by(Request.current_status)
    )
    requests_by_status_result = db.execute(requests_by_status_stmt).all()
    requests_by_status = {status.value: count for status, count in requests_by_status_result}

    # Total de usuarios
    total_users_stmt = select(func.count()).select_from(User)
    total_users = db.execute(total_users_stmt).scalar() or 0

    # Notificaciones no leídas
    unread_notifications_stmt = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.is_read == False)
    )
    unread_notifications = db.execute(unread_notifications_stmt).scalar() or 0

    return {
        "total_requests": total_requests,
        "requests_by_status": requests_by_status,
        "total_users": total_users,
        "unread_notifications": unread_notifications,
    }
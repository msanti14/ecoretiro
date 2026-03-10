"""
Servicio de Dashboard: lógica de negocio para estadísticas de admin.
Delega en dashboard_repository; valida permisos y lanza excepciones.
"""
from sqlalchemy.orm import Session

from backend.repositories import dashboard_repository
from backend.schemas.dashboard_schema import DashboardStats


def get_stats(db: Session) -> DashboardStats:
    """
    Retorna estadísticas del sistema para dashboard de admin.
    Incluye totales de solicitudes, usuarios y notificaciones no leídas.
    """
    stats_dict = dashboard_repository.get_stats(db)
    return DashboardStats(**stats_dict)
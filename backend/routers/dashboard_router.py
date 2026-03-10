"""
Router de Dashboard: endpoints HTTP para estadísticas de admin.
Solo HTTP y delegación a dashboard_service; auth vía core/dependencies.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db, require_role
from backend.models.user_model import User, UserRole
from backend.schemas.dashboard_schema import DashboardStats
from backend.services import dashboard_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> DashboardStats:
    """Retorna estadísticas del sistema (solo para ADMIN)."""
    return dashboard_service.get_stats(db)
"""
Router de Notification: endpoints HTTP para notificaciones internas.
Solo HTTP y delegación a notification_service; auth vía core/dependencies.
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db, get_current_user
from backend.models.user_model import User
from backend.schemas.notification_schema import NotificationOut
from backend.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=list[NotificationOut])
async def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[NotificationOut]:
    """Lista todas las notificaciones del usuario autenticado."""
    return notification_service.get_my_notifications(db, current_user)


@router.patch("/{notification_id}", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> NotificationOut:
    """Marca una notificación como leída (solo si pertenece al usuario)."""
    return notification_service.mark_notification_read(
        db, notification_id, current_user
    )
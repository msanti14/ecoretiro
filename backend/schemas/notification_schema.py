"""
Schemas de Notification: validación de entrada/salida para notificaciones internas.
NotificationOut (readable) y NotificationUpdate (patchable).
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# --- NotificationOut: respuesta de GET /notifications y GET /notifications/{id} ---

class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    request_id: UUID | None
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- NotificationUpdate: body de PATCH /notifications/{id} ---

class NotificationUpdate(BaseModel):
    is_read: bool

"""
Schemas de Dashboard: estadísticas para panel de administración.
DashboardStats: métricas del sistema para usuarios ADMIN.
"""
from pydantic import BaseModel, ConfigDict


# --- DashboardStats: respuesta de GET /admin/stats ---

class DashboardStats(BaseModel):
    total_requests: int
    requests_by_status: dict[str, int]
    total_users: int
    unread_notifications: int
    model_config = ConfigDict(from_attributes=True)
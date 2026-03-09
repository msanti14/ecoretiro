"""agrega tablas requests y status_history

Revision ID: b8b47d6d325e
Revises: a7a36c5c214c
Create Date: 2026-03-08

Tablas: requests (solicitudes de retiro), status_history (historial de estados).
Índice en requests.tracking_number. Sin pérdida de datos (solo tablas nuevas).
Downgrade: borra status_history, requests y tipos ENUM en orden correcto.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8b47d6d325e"
down_revision: Union[str, Sequence[str], None] = "a7a36c5c214c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tipos ENUM existentes en PostgreSQL (create_type=False: solo referenciar, no crear)
MATERIALTYPE = sa.Enum(
    "COMPUTADORA",
    "MONITOR",
    "TELEVISOR",
    "IMPRESORA",
    "CELULAR",
    "TABLET",
    "ELECTRODOMESTICO",
    "CABLE",
    "PLACA_CIRCUITO",
    "PILA_BATERIA",
    "OTRO",
    name="materialtype",
    create_type=False,
)
ESTIMATEDVOLUME = sa.Enum(
    "SMALL", "MEDIUM", "LARGE", name="estimatedvolume", create_type=False
)
PICKUPTIMERANGE = sa.Enum(
    "MORNING", "AFTERNOON", "EVENING", name="pickuptimerange", create_type=False
)
REQUESTSTATUS = sa.Enum(
    "REQUESTED",
    "SCHEDULED",
    "IN_ROUTE",
    "COLLECTED",
    "CLASSIFIED",
    "RECOVERED",
    "SENT_TO_RECYCLING",
    "COMPLETED",
    name="requeststatus",
    create_type=False,
)
VEHICLEASSIGNED = sa.Enum("DUCATO", "AUTO", name="vehicleassigned", create_type=False)


def upgrade() -> None:
    op.create_table(
        "requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tracking_number", sa.String(length=30), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("material_type", MATERIALTYPE, nullable=False),
        sa.Column("estimated_volume", ESTIMATEDVOLUME, nullable=False),
        sa.Column("pickup_date", sa.Date(), nullable=False),
        sa.Column("pickup_time_range", PICKUPTIMERANGE, nullable=False),
        sa.Column(
            "current_status",
            REQUESTSTATUS,
            nullable=False,
            server_default=sa.text("'REQUESTED'::requeststatus"),
        ),
        sa.Column("vehicle_assigned", VEHICLEASSIGNED, nullable=True),
        sa.Column("operator_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"]),
        sa.UniqueConstraint("tracking_number", name="uq_requests_tracking_number"),
    )
    op.create_index(
        "ix_requests_tracking_number",
        "requests",
        ["tracking_number"],
        unique=True,
    )

    op.create_table(
        "status_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("status", REQUESTSTATUS, nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("status_history")
    op.drop_table("requests")

    # Eliminar tipos ENUM (orden: los que no tienen dependencias primero)
    VEHICLEASSIGNED.drop(op.get_bind(), checkfirst=True)
    REQUESTSTATUS.drop(op.get_bind(), checkfirst=True)
    PICKUPTIMERANGE.drop(op.get_bind(), checkfirst=True)
    ESTIMATEDVOLUME.drop(op.get_bind(), checkfirst=True)
    MATERIALTYPE.drop(op.get_bind(), checkfirst=True)

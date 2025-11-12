"""create incidents table

Revision ID: 4f2a9c1d7e3b
Revises:
Create Date: 2025-11-12 20:58:12.408317
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4f2a9c1d7e3b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

incident_source = sa.Enum("operator", "monitoring", "partner", name="incident_source")
incident_status = sa.Enum("new", "in_progress", "resolved", "closed", name="incident_status")


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", incident_source, nullable=False),
        sa.Column("status", incident_status, server_default="new", nullable=False),
        sa.Column("resolution", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_incidents")),
    )
    op.create_index("ix_incidents_status_created_at", "incidents", ["status", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_incidents_status_created_at", table_name="incidents")
    op.drop_table("incidents")
    incident_status.drop(op.get_bind(), checkfirst=True)
    incident_source.drop(op.get_bind(), checkfirst=True)

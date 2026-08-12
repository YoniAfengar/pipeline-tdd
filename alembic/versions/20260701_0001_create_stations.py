"""create stations

Revision ID: 0001
Revises:
Create Date: 2026-07-01
"""
from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE stations (
            station_id text PRIMARY KEY,
            name       text NOT NULL
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE stations")

"""create dock_events

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-01

The foreign key is the point of spec item 3: an event at a station nobody has heard of is refused by
the database, not by an `if` in Python.
"""
from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE dock_events (
            event_id        text        PRIMARY KEY,
            station_id      text        NOT NULL REFERENCES stations (station_id),
            occurred_at     timestamptz NOT NULL,
            bikes_available integer     NOT NULL CHECK (bikes_available >= 0),
            docks_free      integer     NOT NULL CHECK (docks_free >= 0)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE dock_events")

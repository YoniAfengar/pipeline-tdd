"""index dock_events by station and time

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-02

Every dashboard query is "this station, this window". Without this index each of them is a sequential
scan of the whole table.

This revision exists so that Task 3 has something to prove. A fixture that applied only `0001` and
`0002` would build a schema that looks right and is missing the thing production has.
"""
from __future__ import annotations

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX dock_events_station_time_idx ON dock_events (station_id, occurred_at)")


def downgrade() -> None:
    op.execute("DROP INDEX dock_events_station_time_idx")

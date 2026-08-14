"""Spec items 2 and 3."""
from __future__ import annotations

from typing import Iterable

import psycopg

from pipeline.model import DockEvent


def load(conn: psycopg.Connection, events: Iterable[DockEvent]) -> int:
    """Insert `events`; return how many rows the database did not already have."""
    loaded = 0

    for event in events:
        cursor = conn.execute(
            """
            INSERT INTO dock_events (
                event_id,
                station_id,
                occurred_at,
                bikes_available,
                docks_free
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
            """,
            (
                event.event_id,
                event.station_id,
                event.occurred_at,
                event.bikes_available,
                event.docks_free,
            ),
        )

        loaded += cursor.rowcount

    return loaded
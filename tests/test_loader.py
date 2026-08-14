from datetime import datetime, timezone

import psycopg

from pipeline.loader import load
from pipeline.model import DockEvent


def test_load_inserts_new_events(db_conn: psycopg.Connection) -> None:
    events = [
        DockEvent(
            event_id="E-1001",
            station_id="ST-0007",
            occurred_at=datetime(2026, 6, 1, 6, 0, tzinfo=timezone.utc),
            bikes_available=5,
            docks_free=10,
        ),
        DockEvent(
            event_id="E-1002",
            station_id="ST-0031",
            occurred_at=datetime(2026, 6, 1, 6, 5, tzinfo=timezone.utc),
            bikes_available=7,
            docks_free=8,
        ),
    ]

    loaded = load(db_conn, events)

    rows = db_conn.execute(
        """
        SELECT event_id
        FROM dock_events
        ORDER BY event_id
        """
    ).fetchall()

    assert loaded == 2
    assert rows == [("E-1001",), ("E-1002",)]


def test_reload_returns_zero(db_conn: psycopg.Connection) -> None:
    events = [
        DockEvent(
            event_id="E-2001",
            station_id="ST-0007",
            occurred_at=datetime(2026, 6, 1, 7, 0, tzinfo=timezone.utc),
            bikes_available=4,
            docks_free=11,
        ),
        DockEvent(
            event_id="E-2002",
            station_id="ST-0031",
            occurred_at=datetime(2026, 6, 1, 7, 5, tzinfo=timezone.utc),
            bikes_available=6,
            docks_free=9,
        ),
    ]

    first_loaded = load(db_conn, events)
    second_loaded = load(db_conn, events)

    rows = db_conn.execute(
        """
        SELECT event_id
        FROM dock_events
        ORDER BY event_id
        """
    ).fetchall()

    assert first_loaded == 2
    assert second_loaded == 0
    assert rows == [("E-2001",), ("E-2002",)]
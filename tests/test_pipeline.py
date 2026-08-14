import json

import psycopg

from pipeline.model import Report
from pipeline.runner import run


def test_run_loads_valid_rows(
    tmp_path,
    pipeline_db_url: str,
) -> None:
    drop_file = tmp_path / "events.jsonl"

    rows = [
        {
            "event_id": "E-6001",
            "station_id": "ST-0007",
            "occurred_at": "2026-06-01T11:00:00+00:00",
            "bikes_available": 5,
            "docks_free": 10,
        },
        {
            "event_id": "E-6002",
            "station_id": "ST-0031",
            "occurred_at": "2026-06-01T11:05:00+00:00",
            "bikes_available": 7,
            "docks_free": 8,
        },
    ]

    with drop_file.open("w") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")

    report = run(tmp_path, pipeline_db_url)

    with psycopg.connect(pipeline_db_url) as conn:
        loaded_rows = conn.execute(
            """
            SELECT event_id
            FROM dock_events
            WHERE event_id IN (%s, %s)
            ORDER BY event_id
            """,
            ("E-6001", "E-6002"),
        ).fetchall()

    assert report == Report(read=2, loaded=2, rejected=0)
    assert loaded_rows == [("E-6001",), ("E-6002",)]


def test_run_counts_malformed_rows_as_rejected(
    tmp_path,
    pipeline_db_url: str,
) -> None:
    drop_file = tmp_path / "events.jsonl"

    rows = [
        {
            "event_id": "E-7001",
            "station_id": "ST-0007",
            "occurred_at": "2026-06-01T12:00:00+00:00",
            "bikes_available": 5,
            "docks_free": 10,
        },
        {
            "event_id": "E-BAD",
            "station_id": "ST-0031",
            "occurred_at": "not-a-timestamp",
            "bikes_available": 7,
            "docks_free": 8,
        },
        {
            "event_id": "E-7002",
            "station_id": "ST-0031",
            "occurred_at": "2026-06-01T12:10:00+00:00",
            "bikes_available": 6,
            "docks_free": 9,
        },
    ]

    with drop_file.open("w") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")

    report = run(tmp_path, pipeline_db_url)

    with psycopg.connect(pipeline_db_url) as conn:
        loaded_rows = conn.execute(
            """
            SELECT event_id
            FROM dock_events
            WHERE event_id IN (%s, %s, %s)
            ORDER BY event_id
            """,
            ("E-7001", "E-BAD", "E-7002"),
        ).fetchall()

    assert report == Report(read=3, loaded=2, rejected=1)
    assert loaded_rows == [("E-7001",), ("E-7002",)]


def test_run_is_idempotent(
    tmp_path,
    pipeline_db_url: str,
) -> None:
    drop_file = tmp_path / "events.jsonl"

    rows = [
        {
            "event_id": "E-8001",
            "station_id": "ST-0007",
            "occurred_at": "2026-06-01T13:00:00+00:00",
            "bikes_available": 5,
            "docks_free": 10,
        },
        {
            "event_id": "E-8002",
            "station_id": "ST-0031",
            "occurred_at": "2026-06-01T13:05:00+00:00",
            "bikes_available": 7,
            "docks_free": 8,
        },
    ]

    with drop_file.open("w") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")

    first_report = run(tmp_path, pipeline_db_url)
    second_report = run(tmp_path, pipeline_db_url)

    with psycopg.connect(pipeline_db_url) as conn:
        loaded_rows = conn.execute(
            """
            SELECT event_id
            FROM dock_events
            WHERE event_id IN (%s, %s)
            ORDER BY event_id
            """,
            ("E-8001", "E-8002"),
        ).fetchall()

    assert first_report == Report(read=2, loaded=2, rejected=0)
    assert second_report == Report(read=2, loaded=0, rejected=0)
    assert loaded_rows == [("E-8001",), ("E-8002",)]
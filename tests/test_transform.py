from datetime import datetime

import pytest

from pipeline.errors import MalformedRow
from pipeline.model import DockEvent
from pipeline.transform import parse_event


def test_parse_event_happy_path() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:00",
        "bikes_available": 14,
        "docks_free": 6,
    }

    expected = DockEvent(
        event_id="E-000001",
        station_id="ST-0007",
        occurred_at=datetime.fromisoformat("2026-06-01T06:00:00+00:00"),
        bikes_available=14,
        docks_free=6,
    )

    assert parse_event(raw) == expected


def test_parse_event_missing_event_id() -> None:
    raw = {
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:00",
        "bikes_available": 14,
        "docks_free": 6,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)


def test_parse_event_missing_occurred_at() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "bikes_available": 14,
        "docks_free": 6,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)


def test_parse_event_unparseable_occurred_at() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:XX",
        "bikes_available": 14,
        "docks_free": 6,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)


def test_parse_event_missing_bikes_available() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:00",
        "docks_free": 6,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)


def test_parse_event_negative_bikes_available() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:00",
        "bikes_available": -1,
        "docks_free": 6,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)


def test_parse_event_missing_docks_free() -> None:
    raw = {
        "event_id": "E-000001",
        "station_id": "ST-0007",
        "occurred_at": "2026-06-01T06:00:00+00:00",
        "bikes_available": 14,
    }

    with pytest.raises(MalformedRow):
        parse_event(raw)
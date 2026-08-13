"""Spec item 1. Pure: no database, no clock, no filesystem."""
from __future__ import annotations

from datetime import datetime

from pipeline.errors import MalformedRow
from pipeline.model import DockEvent, RawEvent


def parse_event(raw: RawEvent) -> DockEvent:
    """One raw JSON object -> one `DockEvent`, or raise `MalformedRow`."""
    if "event_id" not in raw:
        raise MalformedRow("event_id is missing")

    if "occurred_at" not in raw:
        raise MalformedRow("occurred_at is missing")

    try:
        occurred_at = datetime.fromisoformat(raw["occurred_at"])
    except ValueError as exc:
        raise MalformedRow("occurred_at is not a timestamp") from exc

    if "bikes_available" not in raw:
        raise MalformedRow("bikes_available is missing")

    if raw["bikes_available"] < 0:
        raise MalformedRow("bikes_available cannot be negative")

    if "docks_free" not in raw:
        raise MalformedRow("docks_free is missing")

    if raw["docks_free"] < 0:
        raise MalformedRow("docks_free cannot be negative")

    return DockEvent(
        event_id=raw["event_id"],
        station_id=raw["station_id"],
        occurred_at=occurred_at,
        bikes_available=raw["bikes_available"],
        docks_free=raw["docks_free"],
    )
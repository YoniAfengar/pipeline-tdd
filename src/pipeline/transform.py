"""Spec item 1. Pure: no database, no clock, no filesystem."""
from __future__ import annotations

from datetime import datetime

from pipeline.model import DockEvent, RawEvent


def parse_event(raw: RawEvent) -> DockEvent:
    """One raw JSON object -> one `DockEvent`, or raise `MalformedRow`."""
    return DockEvent(
        event_id=raw["event_id"],
        station_id=raw["station_id"],
        occurred_at=datetime.fromisoformat(raw["occurred_at"]),
        bikes_available=raw["bikes_available"],
        docks_free=raw["docks_free"],
    )
"""Spec item 1. Pure: no database, no clock, no filesystem."""
from __future__ import annotations

from datetime import datetime
from typing import cast

from pipeline.errors import MalformedRow
from pipeline.model import DockEvent, RawEvent


def _parse_timestamp(raw: RawEvent) -> datetime:
    if "occurred_at" not in raw:
        raise MalformedRow("occurred_at is missing")
    try:
        return datetime.fromisoformat(raw["occurred_at"])
    except ValueError as exc:
        raise MalformedRow("occurred_at is not a timestamp") from exc


def _parse_count(raw: RawEvent, field: str) -> int:
    if field not in raw:
        raise MalformedRow(f"{field} is missing")
    value = cast(int, raw[field])
    if value < 0:
        raise MalformedRow(f"{field} cannot be negative")
    return value


def parse_event(raw: RawEvent) -> DockEvent:
    """One raw JSON object -> one `DockEvent`, or raise `MalformedRow`."""
    if "event_id" not in raw:
        raise MalformedRow("event_id is missing")

    return DockEvent(
        event_id=raw["event_id"],
        station_id=raw["station_id"],
        occurred_at=_parse_timestamp(raw),
        bikes_available=_parse_count(raw, "bikes_available"),
        docks_free=_parse_count(raw, "docks_free"),
    )
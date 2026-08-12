"""Spec item 1. Pure: no database, no clock, no filesystem."""
from __future__ import annotations

from pipeline.model import DockEvent, RawEvent


def parse_event(raw: RawEvent) -> DockEvent:
    """One raw JSON object -> one `DockEvent`, or raise `MalformedRow`."""
    raise NotImplementedError

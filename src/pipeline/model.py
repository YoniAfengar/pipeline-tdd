"""What moves through the pipeline. Given — do not edit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypeAlias

RawEvent: TypeAlias = dict[str, Any]


@dataclass(frozen=True, slots=True)
class DockEvent:
    event_id: str
    station_id: str
    occurred_at: datetime
    bikes_available: int
    docks_free: int


@dataclass(frozen=True, slots=True)
class Report:
    read: int
    loaded: int
    rejected: int

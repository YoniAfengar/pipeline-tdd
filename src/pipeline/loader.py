"""Spec items 2 and 3."""
from __future__ import annotations

from typing import Iterable

import psycopg

from pipeline.model import DockEvent


def load(conn: psycopg.Connection, events: Iterable[DockEvent]) -> int:
    """Insert `events`; return how many rows the database did not already have."""
    raise NotImplementedError

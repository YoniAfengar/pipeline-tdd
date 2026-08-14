"""Spec items 4, 5 and 6."""
from __future__ import annotations

import json
from pathlib import Path

import psycopg

from pipeline.errors import MalformedRow
from pipeline.loader import load
from pipeline.model import DockEvent, Report
from pipeline.transform import parse_event


def _read_events(drop_dir: Path) -> tuple[list[DockEvent], int, int]:
    events: list[DockEvent] = []
    read = 0
    rejected = 0

    for path in sorted(drop_dir.glob("*.jsonl")):
        with path.open() as file:
            for line in file:
                read += 1
                try:
                    events.append(parse_event(json.loads(line)))
                except MalformedRow:
                    rejected += 1

    return (events, read, rejected)


def run(drop_dir: Path, dsn: str) -> Report:
    """Read every `*.jsonl` in `drop_dir`, transform, load, and report what happened."""
    events, read, rejected = _read_events(drop_dir)

    with psycopg.connect(dsn) as conn:
        loaded = load(conn, events)
        conn.commit()

    return Report(
        read=read,
        loaded=loaded,
        rejected=rejected,
    )
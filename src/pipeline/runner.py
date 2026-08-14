"""Spec items 4, 5 and 6."""
from __future__ import annotations

import json
from pathlib import Path

import psycopg

from pipeline.loader import load
from pipeline.model import DockEvent, Report
from pipeline.transform import parse_event


def run(drop_dir: Path, dsn: str) -> Report:
    """Read every `*.jsonl` in `drop_dir`, transform, load, and report what happened."""
    events: list[DockEvent] = []
    read = 0

    for path in sorted(drop_dir.glob("*.jsonl")):
        with path.open() as file:
            for line in file:
                read += 1
                raw = json.loads(line)
                events.append(parse_event(raw))

    with psycopg.connect(dsn) as conn:
        loaded = load(conn, events)
        conn.commit()

    return Report(
        read=read,
        loaded=loaded,
        rejected=0,
    )
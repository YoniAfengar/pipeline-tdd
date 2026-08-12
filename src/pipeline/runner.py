"""Spec items 4, 5 and 6."""
from __future__ import annotations

from pathlib import Path

from pipeline.model import Report


def run(drop_dir: Path, dsn: str) -> Report:
    """Read every `*.jsonl` in `drop_dir`, transform, load, and report what happened."""
    raise NotImplementedError

"""Given — do not edit. (Naming failures was the previous exercise.)"""
from __future__ import annotations


class PipelineError(Exception):
    """Anything this pipeline raises on purpose."""


class MalformedRow(PipelineError):
    """This row is unusable. The run continues without it."""


class UnknownStation(PipelineError):
    """A batch referenced a station the database has never heard of. Nothing in it was loaded."""

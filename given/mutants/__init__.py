"""Three pipelines that look like they work. Given — do not edit.

Each mutant replaces one file of `src/pipeline/` with a version carrying exactly one real bug. Your
suite is run against each of them, in a copy of your project, and it must **fail** every time. A
mutant your suite lets through is a bug your suite would have let into production.

    uv run python -m given.mutants
"""
from __future__ import annotations

# mutant name -> (module it replaces, what is wrong with it)
MUTANTS: dict[str, tuple[str, str]] = {
    "returns_batch_size": (
        "loader.py", "reports every event as newly inserted, even the ones already there"),
    "swallows_malformed": (
        "runner.py", "skips a malformed row without counting it"),
    "commits_per_row": (
        "loader.py", "commits each event as it goes, so a rejected batch leaves rows behind"),
}

"""Run YOUR suite against three broken pipelines. Given — do not edit.

For each mutant: copy your project to a temp directory, overwrite one file of `src/pipeline/` with the
mutant's version, and run your tests there. Your suite must **fail**. A mutant that survives is a bug
your tests would have let into production.

The control run comes first: your suite against your own code, which must pass. A suite that cannot
pass its own implementation kills every mutant for the wrong reason.

The mutant sources are base64 so that you do not read a working `loader.py` on your way to writing
one. That is not security; it is a courtesy to your future self.
"""
from __future__ import annotations

import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from given.mutants import MUTANTS

HERE = Path(__file__).resolve().parent          # given/mutants/
ROOT = HERE.parents[1]                          # the project root
COPY = ("pyproject.toml", "alembic.ini", "alembic", "given", "src", "tests", "tools")


def _project_copy(work: Path) -> None:
    for name in COPY:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, work / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif source.exists():
            shutil.copy(source, work / name)


def _suite_passes(mutant: str | None) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        _project_copy(work)
        if mutant is not None:
            module, _ = MUTANTS[mutant]
            encoded = (HERE / f"{mutant}.py.b64").read_bytes()
            (work / "src" / "pipeline" / module).write_bytes(base64.b64decode(encoded))
        done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"],
                              cwd=work, capture_output=True, text=True)
        return done.returncode == 0


def main() -> int:
    if not (ROOT / "tests").is_dir():
        print("no tests/ directory — there is nothing to check yet")
        return 1

    print("control: your suite against your own pipeline")
    if not _suite_passes(None):
        print("  [BAD] your own suite does not pass. Fix that first.\n")
        return 1
    print("  [ok ] passes\n")

    survivors = []
    for mutant, (module, bug) in MUTANTS.items():
        killed = not _suite_passes(mutant)
        survivors += [] if killed else [mutant]
        print(f"  [{'ok ' if killed else 'BAD'}] {mutant:20s} {module:10s} {bug}")

    print()
    if survivors:
        print(f"RESULT: {len(survivors)} mutant(s) survived your suite: {', '.join(survivors)}")
        return 1
    print(f"RESULT: {len(MUTANTS)}/{len(MUTANTS)} killed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

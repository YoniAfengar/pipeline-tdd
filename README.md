# TDD Based Project

_A pipeline you would trust on a Friday._

> **This is not the testcontainers exercise you already did.** In `testing/testcontainers-integration`
> you were handed a `conftest.py` and told not to touch it, and a suite that was already written. Here
> you write **both**. The container, the migration run, the seed, the per-test isolation, and every
> test — none of it exists yet. **There is no `tests/` directory in this repo.**

Meridian Bikes has a second feed. Every dock in the city reports its status — how many bikes are
racked, how many empty slots remain — and those reports land as `dock-events-2026-06-01.jsonl`, one
JSON object per line. The ingest for it is three unimplemented functions, and the team wants it in
production.

The rule for production here is simple: **you can deploy it on a Friday afternoon.** Which means the
suite has to tell the truth about a pipeline that reads files, transforms rows, and writes to Postgres
— on your laptop and in CI, identically, with no shared staging database and nothing to clean up
afterwards.

You are going to build it test-first. Not "write the code then add tests." Red, green, refactor,
starting from a behavior spec written in English.

**Budget** ~3h05, including §0. You need `git`, `docker` (running, for testcontainers), `uv`, and
Python 3.11+ on your own machine.

---

## 0. Your repository (~10 min)

This exercise leaves the course. Copy it somewhere on your own machine — **not** into the course repo,
and **not** into the devcontainer.

```bash
cp -R hands-on/practicum/pipeline-tdd ~/projects/pipeline-tdd
cd ~/projects/pipeline-tdd
git init && git add -A && git commit -m "Start from the provided stub"
```

Then create an empty repository on GitHub, `git remote add origin …`, and push.

**Commit after every red and every green.** In this exercise more than any other, the history *is* the
deliverable: a reviewer should be able to read `git log` and see a failing test appear one commit
before the code that makes it pass. A single commit containing a finished pipeline and a finished suite
tells us you did not do the exercise, whatever the tests say.

**You hand in the repository URL**, with `uv run pytest` green, `uv run python -m given.mutants`
reporting 3/3, `uv run mypy src/` clean, and `ANSWERS.md` filled in.

---

## What's given — do not edit

```
given/
  drops/                three .jsonl drops; the last one has malformed rows
  seed/stations.csv     the reference data every event joins against
  mutants/              three deliberately broken pipelines (see Task 7)
alembic.ini
alembic/
  env.py
  versions/             three revisions, already written: stations, dock_events, and an index
src/pipeline/
  model.py              DockEvent, Report                         (given)
  errors.py             PipelineError, MalformedRow, UnknownStation (given)
  transform.py          `def parse_event(raw) -> DockEvent:`      ...NotImplementedError
  loader.py             `def load(conn, events) -> int:`          ...NotImplementedError
  runner.py             `def run(drop_dir, dsn) -> Report:`       ...NotImplementedError
tools/check_loc.py
```

The migrations are given because writing them was the *previous* exercise. What you have never done is
make a test suite apply them to a database that did not exist when the test started.

## The behavior spec

This is the whole specification. It is prose on purpose: **turning a sentence into a failing test is
the skill being checked.** Do not go looking for the assertions; write them.

1. `parse_event` turns one raw JSON object into a `DockEvent`, or raises `MalformedRow`. A row is
   malformed if `event_id` is missing, if `occurred_at` is missing or unparseable, or if a count
   (`bikes_available`, `docks_free`) is missing or negative. Zero is a perfectly good count.
2. `load` inserts events and returns the number **newly** inserted. Loading the same events again
   inserts nothing and returns `0`.
3. `load` refuses a batch containing an event whose `station_id` is not a known station: it raises
   `UnknownStation` and **nothing in that batch is loaded**. *The database enforces this, not Python.*
4. `run` reads every `*.jsonl` in a directory, transforms, loads, and returns a `Report` carrying
   `read`, `loaded`, `rejected`.
5. `run` on a directory containing malformed rows loads the good rows, counts the bad ones as
   rejected, and does not raise.
6. `run` is idempotent: running it twice over the same directory leaves the table as it was after the
   first run, and the second run reports `loaded == 0`.

---

## Task 1 — One red test, no database (~20 min)

Create `tests/test_transform.py`. Write **one** failing test for spec item 1 — the happy path, nothing
else. Run it. Watch it fail with `NotImplementedError`. Now make it pass.

That loop is the exercise. Everything below is the same loop at larger radius.

**Done when** one test is green and you have not written a line of `loader.py`.

---

## Task 2 — Drive out the transform (~25 min)

Still no database. Spec item 1 has several failure modes; each is a red test before it is a green one.
Add them one at a time. Do not forget the row that is *not* malformed: a rack with zero bikes is the
most interesting event a dock reports.

**Done when** `tests/test_transform.py` covers the happy path and every malformed case, and
`transform.py` is complete. Every one of those tests must run in **milliseconds** — if any of them
needs a container, you have put logic in the wrong place.

> Notice what just happened: the fastest and most numerous tests attached themselves to the pure
> function. That is not a coincidence you engineered — it is what a pure function *is*.

---

## Task 3 — A database that did not exist a second ago (~30 min)

Create `tests/conftest.py`. Write a **session-scoped** fixture that starts a `postgres:16-alpine`
container and then, against it, builds the schema the way production builds it:

```bash
alembic upgrade head
```

Not `schema.sql`. Not `CREATE TABLE` inline in the fixture. **The real Alembic revisions**, driven from
the fixture, pointed at the container's URL — because a suite that builds its schema differently from
production is a suite that lies about production. If revision 3 is broken, this suite must be the thing
that finds out.

**Done when** a throwaway test asserts that `stations` and `dock_events` both exist, **and** that the
index added by the third revision is present — so if it passes, your fixture really did apply all
three, in order.

<details>
<summary>Stuck on the plumbing?</summary>

`PostgresContainer("postgres:16-alpine", driver=None)` as a context manager gives you a URL that
`psycopg` can use directly. Alembic has a Python API — `alembic.config.Config` and
`alembic.command.upgrade(cfg, "head")` — so you never shell out. Read `alembic/env.py` to see where it
expects the URL to come from.

Session scope, because starting Postgres and migrating it costs seconds and you are about to have
twenty tests.
</details>

---

## Task 4 — Isolation without a truncate (~20 min)

One container, twenty tests, and no test may see another's rows.

The cheap answer is `TRUNCATE` between tests. Use the better one: give each test a connection inside a
transaction that is **rolled back** when the test ends. Nothing is ever committed; nothing needs
cleaning; two tests could run in either order.

**Done when** two tests each insert the same `event_id` and both pass, in either order.

**Then answer in `ANSWERS.md` (3–5 sentences):** name one thing the rollback strategy cannot test that
`TRUNCATE` can.

That question is not rhetorical, and you are going to walk into it in Task 6. Rollback isolation works
only for as long as the code under test never commits. The moment `load` opens a transaction of its
own and commits it, your teardown has nothing left to undo — and the failure does not appear in the
test that caused it. It appears in the *next* one, as a row that should not exist.

---

## Task 5 — Seed the reference data (~20 min)

Spec item 3 says the database refuses an event whose `station_id` is unknown. For that sentence to have
any meaning, some stations have to be **known**. `given/seed/stations.csv` is that list — the real one,
the same file production loads.

This is **reference data**, and it is a different animal from the rows your tests create:

- *Test data* is what a single test invents to make its point — two events, one duplicate — and it
  should vanish when that test ends. Task 4's rollback does exactly that.
- *Reference data* is part of the world the tests run in. Every test assumes stations exist. No test
  created them, none should delete them, and none should have to.

So the seed loads **once per session**, right after `alembic upgrade head`, and it is **committed** —
which puts it in a genuinely awkward place, and noticing that is the point of this task. Task 4's
per-test transactions roll back, so anything they wrote disappears. If you seed inside one of those
transactions, the stations vanish with it and every foreign-key test starts failing for a reason that
has nothing to do with foreign keys. Seed on a connection of its own, commit, and let the per-test
transactions layer on top of a database that already has stations in it.

Two ordering constraints follow, and your fixture graph has to honour both: the seed cannot run before
the migrations (no table), and no test connection may open before the seed commits (no stations).

Express both as **fixture dependencies**, not as `autouse` and not as test ordering. A fixture that
depends on another is how pytest spells "after".

**Done when** a test asserts a known station id from the CSV is present, and your suite still runs in
about the same wall-clock time as it did before Task 5 — if it got slower, you are re-seeding per test.

**Then answer in `ANSWERS.md` (3–5 sentences):** you could have put the `INSERT`s for `stations.csv`
inside migration 1, and then the seed would need no fixture at all. Some teams do exactly that. Give one
concrete argument for it and one against, and say which you would choose for *this* table.

---

## Task 6 — The loader, against a real database (~30 min)

`tests/test_loader.py`, then `src/pipeline/loader.py`. Spec items 2 and 3.

Item 3 is the interesting one: *"the database enforces this, not Python."* Write the test that proves
it. If you can make that test pass by adding an `if` to `loader.py` — reading the station list and
filtering — you have written the wrong test, and one of the hidden mutants will say so. (Think about
what happens between your `SELECT` and your `INSERT`.)

Item 3 also says **nothing in that batch is loaded**. Write the test where the bad event is *last*, so
that everything before it looked fine on the way in.

And now Task 4's question comes for you. Whatever `load` does, it must not commit — the caller owns the
transaction. Prove it: after `load`, open a *second* connection and assert it sees nothing. If that
assertion fails, your per-test isolation was a fiction and half your suite has been passing on rows
left behind by the test before it.

**Done when** both spec items are green, including the re-load returning `0`.

---

## Task 7 — The whole pipeline, and the suite that checks your suite (~30 min)

`tests/test_pipeline.py`, then `src/pipeline/runner.py`. Spec items 4, 5, 6.

`run` opens its own connection and commits. Which means the rollback fixture cannot isolate it, and you
will need a different fixture for these tests. You already know why.

Then run the mutant check:

```bash
uv run python -m given.mutants          # runs YOUR suite against three broken pipelines
```

Each mutant is a working-looking pipeline with one real bug: one reports every event as newly inserted,
one silently skips malformed rows without counting them, one commits as it goes so a rejected batch
leaves rows behind. **Your suite must fail against every one of them.** A mutant that survives is a bug
your tests would have let into production.

Notice what all three have in common: **none of them can be caught by looking at the table.** The rows
end up right. What is wrong is a number in a `Report` that nobody ever asserted on — which is precisely
what a suite written *after* the code forgets to check, because the code is already returning it.

**Done when** all three mutants are killed and your suite is green against your own implementation.

> Three mutants ship with the exercise so you can self-check. Your instructor has more. A suite tuned to
> kill exactly the three you can see is a suite tuned to the wrong thing.

---

## The size gate

Write `tests/test_size.py` yourself, in one line, by importing the vendored checker
(`from check_loc import find_violations`): functions in `src/pipeline/` ≤ **20** code lines, files ≤
**250**. It does not check `tests/`.

`run()` is where it bites. Reading a directory, transforming, counting rejects, loading, and tallying a
report does not fit in twenty lines, and it should not: each of those is a thing you might want to test
alone. The limit is telling you where the seams are — and because you wrote the tests first, you will
find the seams are already exactly where your test names are.

## Done when

```bash
uv run pytest                    # green, container and all
uv run python -m given.mutants   # 3/3 killed
uv run mypy src/
```

`ANSWERS.md` answers Tasks 4 and 5. And you can say, out loud, why nothing in `tests/` needed a running
Postgres before you started one.

## Why this matters

Most test suites are written after the code, and they encode what the code *does* rather than what it
was *supposed to do*. You can see it in the failure mode: the suite is green, the pipeline double-loads
every retried drop, and nobody notices for two days.

Writing the test first is the cheapest way to keep the spec and the suite the same object. Running your
suite against deliberately broken code is the cheapest way to find out whether it worked.

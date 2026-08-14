# Pipeline TDD

![Pipeline TDD Hero](assets/hero.png)

A production-style data pipeline built test-first, with real PostgreSQL integration, transaction-aware test isolation, mutation testing, and strict source-size limits.

The project ingests dock-event JSONL files, validates and transforms each row, writes valid events to PostgreSQL, rejects malformed input safely, and guarantees idempotent reprocessing.

The core goal was not only to make the pipeline work, but to build a test suite strong enough to prove that it works.

---

## What This Project Demonstrates

- Test-Driven Development using a real RED → GREEN → REFACTOR workflow
- Pure transformation logic tested independently from infrastructure
- PostgreSQL integration using Testcontainers
- Real Alembic migrations applied inside the test environment
- Transaction rollback isolation for database tests
- TRUNCATE-based isolation where committed transactions make rollback insufficient
- Database-enforced foreign key integrity
- Idempotent event loading
- Malformed-row handling without failing the whole pipeline
- Mutation testing to verify test-suite quality
- Source-size enforcement to keep functions focused and maintainable

---

## Pipeline Flow

```text
JSONL drop files
       │
       ▼
     run()
       │
       ├── reads every *.jsonl file
       │
       ▼
 parse_event()
       │
       ├── validates required fields
       ├── parses timestamps
       └── rejects malformed rows
       │
       ▼
     load()
       │
       ├── inserts valid events
       ├── ignores duplicate event_ids
       ├── relies on PostgreSQL foreign keys
       └── leaves transaction ownership to the caller
       │
       ▼
   PostgreSQL
       │
       ▼
Report(read, loaded, rejected)
```

---

## Test-Driven Development

The implementation was built incrementally from behavior specifications.

For each new behavior:

```text
RED
Write a failing test

↓

GREEN
Write the minimum implementation required to pass

↓

REFACTOR
Improve the design while keeping the suite green
```

The Git history preserves this process, including separate failing-test and implementation commits.

Examples include:

- missing or invalid event fields
- duplicate event loading
- unknown station handling
- transaction ownership
- malformed rows inside a complete pipeline run
- repeated pipeline execution

---

## Test Suite

The final suite contains tests across four layers:

```text
Transform tests
    ↓
Loader integration tests
    ↓
Database / migration tests
    ↓
End-to-end pipeline tests
```

It also includes a source-size gate that limits functions to 20 code lines and files to 250 code lines.

![Test Suite](assets/screenshots/test-suite.png)

```text
23 passed
```

The suite starts a real temporary PostgreSQL instance, applies the real Alembic migrations, seeds reference data, executes the tests, and removes the container afterward.

No shared staging database is required.

---

## Mutation Testing

A passing test suite is not enough if the tests would also pass against broken code.

The project therefore runs the suite against three intentionally defective pipeline implementations.

![Mutation Testing](assets/screenshots/mutation-testing.png)

```text
returns_batch_size   → killed
swallows_malformed   → killed
commits_per_row      → killed

RESULT: 3/3 killed
```

### What the Mutants Test

**`returns_batch_size`**

Incorrectly reports every event as newly inserted, including duplicates.

Killed by:

```text
test_run_is_idempotent
```

**`swallows_malformed`**

Skips malformed rows without incrementing the rejected count.

Killed by:

```text
test_run_counts_malformed_rows_as_rejected
```

**`commits_per_row`**

Commits events individually, allowing part of a rejected batch to remain in the database.

Killed by:

```text
test_unknown_station_rejects_entire_batch
```

This verifies not only final database state, but also externally observable pipeline behavior and transaction guarantees.

---

## Database Testing Strategy

### PostgreSQL with Testcontainers

The test suite starts a temporary:

```text
postgres:16-alpine
```

container for the entire test session.

The database does not exist before the suite begins and is discarded when the suite ends.

### Real Alembic Migrations

The schema is created using the same migration path expected in production:

```bash
alembic upgrade head
```

The tests verify that:

- `stations` exists
- `dock_events` exists
- the revision-3 station/time index exists

This ensures the tests do not silently use a schema that differs from production.

---

## Test Isolation

Two different isolation strategies are used deliberately.

### Rollback Isolation

Most database tests receive a connection inside a transaction.

After each test:

```text
ROLLBACK
```

removes all test-created rows.

This is fast and avoids repeated cleanup.

### TRUNCATE Isolation

The end-to-end `run()` function opens its own connection and commits.

Once code under test commits, an outer fixture cannot undo those changes with rollback.

Pipeline tests therefore use:

```text
TRUNCATE dock_events
```

before and after each test.

This distinction reflects real transaction behavior rather than hiding it from the suite.

---

## Reference Data

Station data comes from:

```text
given/seed/stations.csv
```

It is loaded once per test session after the migrations and committed independently from test-generated data.

This keeps reference data separate from per-test data and allows the same station file to represent the environment used by both production-style code and tests.

---

## Data Integrity

Unknown stations are rejected by PostgreSQL itself through a foreign key.

The loader does not first query the station table and manually validate the ID.

Instead:

```text
INSERT
   ↓
PostgreSQL foreign key
   ↓
ForeignKeyViolation
   ↓
UnknownStation
```

This avoids introducing a race between a separate validation query and the actual insert.

---

## Idempotency

Events use `event_id` as their unique identifier.

Loading an existing event again uses:

```sql
ON CONFLICT (event_id) DO NOTHING
```

The loader reports the number of rows actually inserted.

Therefore:

```text
First run
loaded = N

Second run over the same files
loaded = 0
```

while the database remains unchanged.

---

## Malformed Rows

Malformed rows do not terminate the entire pipeline.

Examples include:

- missing `event_id`
- missing `occurred_at`
- invalid timestamps
- missing count fields
- negative bike or dock counts

A malformed event contributes to `rejected`, while valid rows in the same drop continue through the pipeline.

Zero is treated as a valid count.

---

## Project Structure

```text
pipeline-tdd/
├── alembic/
│   ├── env.py
│   └── versions/
│
├── assets/
│   ├── hero.png
│   └── screenshots/
│       ├── mutation-testing.png
│       └── test-suite.png
│
├── given/
│   ├── drops/
│   ├── mutants/
│   └── seed/
│       └── stations.csv
│
├── src/
│   └── pipeline/
│       ├── errors.py
│       ├── loader.py
│       ├── model.py
│       ├── runner.py
│       └── transform.py
│
├── tests/
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_loader.py
│   ├── test_pipeline.py
│   ├── test_size.py
│   └── test_transform.py
│
├── tools/
│   └── check_loc.py
│
├── ANSWERS.md
├── alembic.ini
├── pyproject.toml
└── uv.lock
```

---

## Tech Stack

- Python
- Pytest
- PostgreSQL
- Psycopg
- Testcontainers
- Docker
- Alembic
- Mypy
- uv
- Git
- GitHub

---

## Running the Project

### Requirements

You need:

- Python 3.11+
- Docker
- uv
- Git

Docker must be running because the integration tests create a temporary PostgreSQL container.

### Install Dependencies

```bash
uv sync
```

### Run the Full Test Suite

```bash
uv run pytest
```

Expected result:

```text
23 passed
```

### Run Mutation Testing

```bash
uv run python -m given.mutants
```

Expected result:

```text
RESULT: 3/3 killed
```

### Run Type Checking

```bash
uv run mypy src/
```

---

## Engineering Decisions

Several design decisions from the project are documented in more detail in [`ANSWERS.md`](ANSWERS.md), including:

- rollback isolation vs. TRUNCATE
- reference data in migrations vs. seed fixtures
- the trade-off introduced by testing exception chains
- which tests killed each mutation

---

## Key Takeaway

The most important outcome of this project is not simply that the pipeline passes its tests.

It is that the tests were designed from the required behavior first, then challenged against deliberately broken implementations.

That makes the suite part of the system's design rather than an after-the-fact verification layer.

```text
23 passing tests
3/3 mutants killed
Real PostgreSQL
Real migrations
Isolated test runs
Idempotent loading
```

**A pipeline you can trust on a Friday.**
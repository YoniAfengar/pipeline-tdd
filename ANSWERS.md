# Answers

Fill this in as you go. It is checked, and it is where the actual understanding shows.

## Task 4 — what rollback isolation cannot test

Name one thing the rollback strategy cannot test that `TRUNCATE` can.

(When you reach Task 6 and this stops being hypothetical, come back and add a sentence about what
actually happened.)


Rollback isolation cannot properly test code that commits its own transaction. Once the code under test commits, the fixture’s rollback can no longer undo those changes. The committed rows can leak into the next test and break test isolation. A TRUNCATE-based cleanup can remove those rows even after they have been committed.

## Task 5 — reference data in the migration, or in a fixture?

You could have put the `INSERT`s for `stations.csv` inside migration 1, and then the seed would need no
fixture at all. Some teams do exactly that.

- One concrete argument **for**: Putting the station inserts in the migration guarantees that the reference data is created together with the schema, with no separate seed step.
- One concrete argument **against**: It couples reference data to schema history, making changes to the station list require database migrations even when the schema itself has not changed.
- What I would choose for *this* table, and why: I would keep `stations.csv` as a separate seed because the station list is reference data that can change independently of the database schema, and the same real file can be loaded by both production and the test suite.



## Task 7 — the mutants

For each mutant, name the single test in your suite that killed it. If the same test killed two of
them, say so — and say whether that worries you.

| mutant | the test that killed it |
|---|---|
| `returns_batch_size` | |
| `swallows_malformed` | |
| `commits_per_row` | |

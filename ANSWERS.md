# Answers

Fill this in as you go. It is checked, and it is where the actual understanding shows.

## Task 4 — what rollback isolation cannot test

Name one thing the rollback strategy cannot test that `TRUNCATE` can.

(When you reach Task 6 and this stops being hypothetical, come back and add a sentence about what
actually happened.)

## Task 5 — reference data in the migration, or in a fixture?

You could have put the `INSERT`s for `stations.csv` inside migration 1, and then the seed would need no
fixture at all. Some teams do exactly that.

- One concrete argument **for**:
- One concrete argument **against**:
- What I would choose for *this* table, and why:

## Task 7 — the mutants

For each mutant, name the single test in your suite that killed it. If the same test killed two of
them, say so — and say whether that worries you.

| mutant | the test that killed it |
|---|---|
| `returns_batch_size` | |
| `swallows_malformed` | |
| `commits_per_row` | |

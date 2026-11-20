# Adoption format: declaring a repo's pattern-adoption state

Every estate repo declares its relationship to the pattern canon in a
`PATTERN_ADOPTION.md` at the repo root, even when the declaration is
empty. The declaration is machine-checked by
`pattern-standards/scripts/adoption-check.py` (CONTEXT-CORE CX-4/CX-5:
IDs resolve, statuses are closed-vocabulary, evidence exists).

## The table

One row per pattern with a real relationship to the repo. Format:

```markdown
| Pattern | Status | Evidence |
|---|---|---|
| T13 | adopted | src/lib.rs:1 (pure cores; middleware is the shell) |
| P51 | planned | breaker integration, tracking issue #14 |
| P57 | refused | R2 (single-team monorepo, T6 codegen binds both sides) |
```

## Rules

1. **Statuses are a closed vocabulary**: `adopted` (in the code, with
   evidence), `partial` (adopted for some paths, noted), `planned`
   (scheduled, with a tracking reference), `refused` (with a refusal id
   R1-R12 or a written reason), `n/a` (domain never applies).
2. **Evidence for adopted/partial**: a file path (with optional `:line`,
   optionally followed by a parenthetical note) that exists. A claim
   without a path is a violation.
3. **Refused rows must cite** a canon refusal id or a written reason;
   refusals are decisions, not omissions.
4. **Planned rows are dated** in the Evidence column (target quarter or
   tracking issue); a plan without a date is a wish (refusal-shaped).
5. **The file is checked, not read**: any ID that does not resolve in
   the canon catalog fails the gate (stale-ID drift is how adoption
   files die).
6. Baseline-tier patterns that do not apply to the repo are omitted
   entirely (the gate for omission is the repo ADR per PATTERN-CORE §5,
   not a row here).

## Nightly soak (X5/property-test crates)

Repos with conservation/property invariants add a scheduled workflow
running the property suite with an enlarged case count (e.g.
`PROPTEST_CASES=4096`), separate from push CI. This satisfies the
ADR-0001 "continuous fuzz" wording: each nightly run is one window in
the cumulative evidence.

## Canon repos

A standards canon carries no runtime patterns; it declares itself with
a leading `<!-- adoption: canon -->` marker and an empty table. The
checker passes with a note instead of requiring rows.

## Drafting with route.py --adopt

For a repo matching a decision-graph node, `scripts/route.py --adopt <NODE>
--repo <path>` drafts `PATTERN_ADOPTION.md` with that node's mandatory
set as `planned` rows (idempotent; existing rows are kept). The drafter
does not verify against code: promote rows to `adopted` only with real
evidence paths per the rules above, and delete rows the code refutes.

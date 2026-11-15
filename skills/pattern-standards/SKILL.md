---
name: wyattau-patterns
description: |
  Route design decisions through the WyattAu pattern canon: 136 constructs,
  8 refusals, 25 baseline-tier defaults, and a 24-node task graph that
  picks patterns for you. Use when choosing or reviewing architecture,
  data flow, or API design; when a failure mode names its pattern
  (N+1, race, deadlock, IDOR, penny rounding, retry storm, prompt
  injection); or on "which pattern for X". Does not: UI aesthetics
  (estate-design), debugging (estate-rigor-loop), SEO (estate-seo).
allowed-tools: read, grep, bash
license: Apache-2.0
---

# wyattau-patterns

Canon: [`WyattAu/pattern-standards`](https://github.com/WyattAu/pattern-standards)
(PATTERN-CORE.md); `references/` is a vendored projection
(PROVENANCE.yml, SC-11). Fix the canon, rebuild the projection — never
hand-edit `references/` here.

## Doctrine

Every canon pattern removes a failure mode from human vigilance and
embeds it in a type, an algebraic operator, a compiler pass, or a
runtime invariant. "Remember to check X" is a scheduled incident, not a
control. Three series: **T** foundations T1–T50 (proven primitives,
default-adopt where domain applies), **P** field constructs P1–P50
(problem-driven, adopt only on the named trigger), **X** frontier X1–X7
(pilot + ADR only).

## Routing: task type first, then failure mode

1. Classify the task into a decision-graph node (N01 paginated API,
   N02 write endpoint, N03 money movement, N04 workflow, N05 agent tool
   call, N06 cache, N07 HTTP client, N08 worker pool, N09 scheduler,
   N10 authz, N11 telemetry, N12 config/flags, N13 migration, N14
   client state, N15 numerical kernel, N16 distributed state, N17 repo
   skeleton, N18 load control, N19 webhook receiver, N20 backfill job,
   N21 risky release, N22 test suite, N23 API surface, N24 deploy).
2. Open `references/decision-graph.md` at that node. Its MANDATORY set,
   ASK branches, and REFUSE edges are the design; do not weigh
   alternatives. An ASK predicate you cannot answer from the task
   requirements goes to the user as a question.
3. No node fits the task? Route by failure mode below.

## Route by failure mode

| Symptom | Load | IDs |
|---|---|---|
| New service, API, or data model | `references/PATTERN-CORE.md` §3 + §5 | baseline tier |
| Pagination skips/duplicates | `references/field-fullstack.md` | P7, R5 |
| API versioning, webhook corruption | `references/field-fullstack.md` | P1, P9 |
| Money splits, unit mixing, lookahead bias | `references/field-numerical.md` | P11–P13 |
| Quote staleness, feed drift, replay divergence | `references/field-numerical.md` | P16, P18, P20 |
| Races, deadlocks, GC tails, noisy tenants | `references/field-concurrency.md` | P22, P25–P26 |
| Retry storms, overload, cold starts | `references/field-concurrency.md` | P24, P27–P28 |
| Cache staleness, untestable faults | `references/field-concurrency.md` | P21, P29 |
| Agent loops, spend blowups, prompt injection | `references/field-agentic.md` | P31–P40 |
| IDOR, log noise, undeletable PII, config tears | `references/field-security.md` | P41–P43, P47 |
| Down dependency down, one pool starving all | `references/field-operations.md` | P51, P52 |
| Poisoned queue, forged webhooks, dropped deploys | `references/field-operations.md` | P53, P54, P62 |
| Traces that will not correlate | `references/field-operations.md` | P63 |
| Lost updates between concurrent writers | `references/field-data-evolution.md` | P55 |
| Backfills, ID strategy, scan-heavy dashboards | `references/field-data-evolution.md` | P56, P60, P61 |
| Provider broke consumers; legacy rewrite | `references/field-data-evolution.md` | P57–P59 |
| Designing the test suite for a module | `references/field-testing.md` | P64–P69 |
| Public API shape, errors, list params, deprecation | `references/field-api.md` | P70–P74 |
| Canary, blue-green, shadow, artifact attestation | `references/field-deployment.md` | P75–P79 |
| Distributed consistency, tail latency | `references/foundations-distributed.md` | T31–T42 |
| Event history, audit, time-travel queries | `references/foundations-state.md` | T21–T30 |
| LLM output validation, agent writes | `references/foundations-interfaces.md` | T48–T50 |
| "Should I add a factory/interface?" | `references/PATTERN-CORE.md` §4, `references/frontier.md` | R1–R3, X7 |
| Uncertainty, spec-as-source, choreography | `references/frontier.md` | X1–X7 |

Full catalog tables with maturity stamps: PATTERN-CORE §6–§8.

## Baseline tier (default-adopt where domain applies)

T1, T11, T13, T19, T27, T32, T33, T36, T43, T48, T49, T50, P4, P7,
P8, P11, P12, P23, P24, P31, P35, P39, P41, P42, P51. Omitting one
needs an ADR stating why the failure mode cannot occur (PATTERN-CORE
§5).

## Refusals (short form; full table in PATTERN-CORE §4)

1. No speculative family factories — extract mechanically when the
   second implementation exists (X7 doctrine).
2. No mock-driven seams for testing's sake — pure core + integration/DST.
3. No runtime inheritance ceremony where a closure or record suffices.
4. No mutable authority columns — derived balances (T27), capabilities (T8).
5. No offset pagination — keyset snapshot cursors (P7).
6. No pattern adoption without a named failure mode.
7. No scattered decision thresholds — one collapse boundary (X1).
8. No criticality vocabularies where everything is P0.

## Adoption rules

1. Find patterns by the Failure line, not the name.
2. Baseline tier is default-adopt; deviations need an ADR.
3. Field (P) adoption records the observed trigger in an ADR first.
4. Frontier (X) is pilot-only: one bounded pilot + ADR; no estate repo
   depends on an X-pattern before a second successful pilot.

## Anti-patterns

- Hand-editing `references/` here — it is a projection; edit the canon
  and rerun `standards-dist/build.sh` (SC-11).
- Citing a pattern ID that does not resolve — grep the ID in the canon
  before referencing it.
- Reaching for X-series constructs in production paths without a
  completed pilot ADR.
- Treating maturity stamps as endorsements: `Speculative` means watch,
  not adopt.

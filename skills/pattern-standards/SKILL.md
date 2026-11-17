---
name: wyattau-patterns
description: |
  Route design decisions through the WyattAu pattern canon: 176 constructs,
  12 refusals, 25 baseline-tier defaults, and a 31-node task graph that
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
(PROVENANCE.yml, SC-11). Fix the canon, rebuild the projection; never
hand-edit `references/` here.

## Doctrine

Every canon pattern removes a failure mode from human vigilance and
embeds it in a type, an algebraic operator, a compiler pass, or a
runtime invariant. "Remember to check X" is a scheduled incident, not a
control. Three series: **T** foundations T1–T50 (proven primitives,
default-adopt where domain applies), **P** field constructs P1–P50
(problem-driven, adopt only on the named trigger), **X** frontier X1–X7
(pilot + ADR only).

## Routing: script first, then graph, then failure mode

1. Traverse in one call: `python3 scripts/route.py --task "<task>"`
   (vendored; parses decision-graph.md and prints the node's M/A/R
   block; exit 1 lists candidates and states the union rule).
2. Script ambiguous? Open `references/decision-graph.md` §node index
   and classify by hand; multi-node tasks union their M sets.
3. No node fits the task? Route by failure mode below. The MCP
   `standards_route` tool delegates to the canon routers from any
   session.

## Adoption declarations (M2)

Repos declare pattern relationships in a root `PATTERN_ADOPTION.md`
(format: `references/adoption-format.md`), validated by
`scripts/adoption-check.py`. Generate or update it when a user asks
whether a repo adopts a pattern; claims without evidence paths fail.

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
| Upstream tables lie to dashboards | `references/field-data-evolution.md` | P110 |
| Backfills, ID strategy, scan-heavy dashboards | `references/field-data-evolution.md` | P56, P60, P61 |
| Provider broke consumers; legacy rewrite | `references/field-data-evolution.md` | P57–P59 |
| Designing the test suite for a module | `references/field-testing.md` | P64–P69, P109 |
| Public API shape, errors, list params, deprecation | `references/field-api.md` | P70–P74 |
| Canary, blue-green, shadow, artifact attestation | `references/field-deployment.md` | P75–P79, P98 |
| PII storage, consent, DSAR, audit tamper-proofing | `references/field-compliance.md` | P80–P86 |
| Order slicing, routing, fills, TCA, kill switch | `references/field-execution.md` | P87–P92 |
| Calls hang, DNS lies, crons double-run | `references/field-networking.md` | P103–P105 |
| DB sessions, double-apply, replica lag | `references/field-data-layer.md` | P106–P108 |
| Skew, model archaeology, lying experiments | `references/field-ml.md` | P111–P113 |
| Degraded modes, watchdogs, voting, margin budgets, cost budgets | `references/field-safety.md` | P93–P95, P100, P119 |
| Restores never tested, metrics exploding | `references/field-operations.md` | P117, P118 |
| Tokens accepted on faith, uploads trusted | `references/field-security.md` | P114–P116 |
| Verifier discipline, golden rot, MC/DC gates | `references/field-verification.md` | P96–P99 |
| Distributed consistency, tail latency | `references/foundations-distributed.md` | T31–T42 |
| Event history, audit, time-travel queries | `references/foundations-state.md` | T21–T30 |
| LLM output validation, agent writes | `references/foundations-interfaces.md` | T48–T50 |
| "Should I add a factory/interface?" | `references/PATTERN-CORE.md` §4, `references/frontier.md` | R1–R3, X7 |
| Uncertainty, spec-as-source, choreography | `references/frontier.md` | X1–X7 |

Full catalog with maturity stamps: `references/catalog.md`.

## Baseline tier (default-adopt where domain applies)

T1, T11, T13, T19, T27, T32, T33, T36, T43, T48, T49, T50, P4, P7,
P8, P11, P12, P23, P24, P31, P35, P39, P41, P42, P51. Omitting one
needs an ADR stating why the failure mode cannot occur (PATTERN-CORE
§5).

## Refusals (short form; full table in PATTERN-CORE §4)

1. No speculative family factories; extract mechanically when the
   second implementation exists (X7 doctrine).
2. No mock-driven seams for testing's sake; pure core + integration/DST.
3. No runtime inheritance ceremony where a closure or record suffices.
4. No mutable authority columns; derived balances (T27), capabilities (T8).
5. No offset pagination; keyset snapshot cursors (P7).
6. No pattern adoption without a named failure mode.
7. No scattered decision thresholds; one collapse boundary (X1).
8. No criticality vocabularies where everything is P0.
9. No org-process patterns; process canon territory.
10. No framework-specific idioms; framework canons own them.
11. No hardware co-design (no bare-metal latency estate yet).
12. No experiment peeking without a pre-registered design (P113).

## Adoption rules

1. Find patterns by the Failure line, not the name.
2. Baseline tier is default-adopt; deviations need an ADR.
3. Field (P) adoption records the observed trigger in an ADR first.
4. Frontier (X) is pilot-only: one bounded pilot + ADR; no estate repo
   depends on an X-pattern before a second successful pilot.

## Anti-patterns

- Hand-editing `references/` here; edit the canon, rerun `build.sh` (SC-11).
- Citing an ID that does not resolve; grep the canon first.
- X-series constructs in production without a completed pilot ADR.
- Maturity stamps are not endorsements; `Speculative` means watch.

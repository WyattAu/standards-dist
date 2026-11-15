# PATTERN-CORE; the WyattAu design-pattern canon

Status: CURRENT, 2026-11. 176 patterns in three series, 12 named
refusals, a 25-pattern baseline tier. Projection source for the
`wyattau-patterns` skill; consumable directly with `references/`.

## 1. Doctrine

Every pattern in this canon removes a failure mode from human
vigilance and embeds it in a type, an algebraic operator, a compiler
pass, or a runtime invariant. "Remember to check `tenant_id`",
"remember to sanitize logs", "remember not to mutate `balance`" are
not engineering controls; they are scheduled incidents. A pattern that
requires discipline is a wish, not a construct; this canon only
admits constructs.

Classic GoF patterns stagnated because they all presuppose the same
box: manually authored, discrete, deterministic text files running on
isolated nodes, defended against future text edits. The series below
escape that box by breaking one of four assumptions:

| Broken assumption | Escaped by | Series |
|---|---|---|
| Values are epistemically exact; time is implicit | Uncertainty and causality as types | T26, P8, P13, X1, X6 |
| State mutates in place; any mutation is representable | Conservation and capability algebra | T8, T27, P41, X5 |
| Execution is single-node, synchronous, infallible | Distribution, failure, and replay as structure | T19, T31–T36, P20, P29 |
| Logic is deterministic text | Probabilistic components with deterministic skins | T48–T50, P31–P40, X2, X4 |

The GoF set is not wrong; Abstract Factory is a record of constructor
closures, Strategy is a function parameter, Decorator is composition,
and most "anti-OOP" codebases contain isomorphic versions. This canon
does not relabel them. It catalogs constructs that change the
computational model, the time model, or the mathematical invariants.
Production prior art for the doctrine exists at API and compiler
scale: Vulkan's explicit-over-implicit design and LLVM's
verify-every-layer discipline are this thesis enforced by platform.

## 2. Series and reading order

| Series | Range | File(s) | Stance |
|---|---|---|---|
| Foundations (T) | T1–T50 | `references/foundations-*.md` | Proven structural primitives; adopt by default where the domain applies |
| Field constructs (P) | P1–P119 | `references/field-*.md` | Problem-driven; adopt when the named failure mode exists |
| Frontier (X) | X1–X7 | `references/frontier.md` | Research-grade; pilot with ADR only |
| Catalog | all | `references/catalog.md` | The full ID enumeration with maturity stamps (mirrors reference headings) |

Field-series domains: `field-fullstack.md` (P1–P10), `field-numerical.md`
(P11–P20), `field-concurrency.md` (P21–P30), `field-agentic.md`
(P31–P40), `field-security.md` (P41–P50, P114–P116), `field-operations.md`
(P51–P54, P62–P63, P101, P117–P118), `field-data-evolution.md` (P55–P61,
P102, P110), `field-testing.md` (P64–P69, P109), `field-api.md` (P70–P74),
`field-deployment.md` (P75–P79, P98), `field-compliance.md` (P80–P86),
`field-execution.md` (P87–P92), `field-safety.md` (P93–P95, P100, P119),
`field-verification.md` (P96–P97, P99), `field-networking.md` (P103–P105),
`field-data-layer.md` (P106–P108), `field-ml.md` (P111–P113). Foundations
domains: types/algebra (T1–T10), execution/reactive (T11–T20),
state/time (T21–T30), distributed (T31–T42), interfaces/security/AI
(T43–T50). Pattern selection per task type is a graph traversal, not a
choice: §6 and `references/decision-graph.md`.

## 3. Baseline tier

Default-adopt in new estate code wherever the domain applies.
Deviations need an ADR.

| ID | Pattern | Applies to |
|---|---|---|
| T1 | Parse, don't validate | every boundary |
| T11 | Structured concurrency | all concurrent code |
| T13 | Functional core, imperative shell | domain logic |
| T19 | Durable replayable coroutines | multi-step orchestration |
| T27 | Double-entry immutable ledger | anything of value |
| T32 | Transactional outbox + CDC | services emitting events |
| T33 | Idempotency barriers | mutating endpoints |
| T36 | Deterministic simulation testing | tier-A kits |
| T43 | Declarative tree reconciliation | all UI |
| T48 | Grammar-constrained decoding | LLM tool calls |
| T49 | Generator + verifier loops | all synthesis |
| T50 | Agentic capability sandboxes | all agents |
| P4 | `Sensitive<T>` redaction | credentials/PII paths |
| P7 | Frozen-snapshot cursor envelopes | all pagination |
| P8 | Dual-frame temporal anchors | future scheduling |
| P11 | Remainder-preserving partition | money splits |
| P12 | Dimensional algebra | quant/accounting kernels |
| P23 | `AbortScope` guards | long-lived processes |
| P24 | Success-refilled retry budgets | HTTP clients |
| P51 | Circuit breaker | outbound clients |
| P31 | Prompt quarantine | agents reading external text |
| P35 | Prefix-pinned KV-cache layouts | multi-turn agents |
| P39 | Inference memoization | multi-stage pipelines |
| P41 | Tenant RLS scopes | multi-tenant services |
| P42 | Wide-event accumulators | all services |

## 4. Refusals

A standard that only lists virtues is not a standard.

| ID | Refusal | Instead |
|---|---|---|
| R1 | Speculative family factories (`IRepositoryFactory` with one implementation) | Concrete code today; extract mechanically when the second implementation exists (X7 doctrine) |
| R2 | Mock-driven interface seams added for testing's sake | Pure cores (T13) + integration/DST (T36); mocks that assert implementation are negative value |
| R3 | Runtime inheritance ceremony where a closure or record suffices | The isomorphic functional form; GoF vocabulary optional |
| R4 | Mutable authority columns (`balance` as stored truth, ambient credentials) | Derived balances over T27; capabilities over T8 |
| R5 | Offset pagination | Keyset snapshot cursors (P7) |
| R6 | Pattern adoption without a named failure mode | Every pattern here names its trigger; no trigger, no adoption |
| R7 | Scattered decision thresholds (`score > 0.8` in 30 services) | One collapse boundary with a stated loss matrix (X1, pilot-tier) |
| R8 | Criticality vocabularies where everything is P0 | Three honest tiers or none (P27) |
| R9 | Org-process patterns (postmortems, design-doc review, on-call rotations) | Process canon lives in AGENTS/SPEC discipline; this canon admits constructs only |
| R10 | Framework-specific idioms (React hook rules, k8s operator patterns) | Framework canons own them; this canon stays framework-free |
| R11 | Hardware co-design (FPGA tick-to-trade, kernel bypass) | Out of scope until the estate runs bare-metal latency paths |
| R12 | Mid-experiment metric peeking without a pre-registered sequential design | P113 provides bucketing and SRM alarms; statistics needs a statistician |

## 5. Adoption procedure

1. Adopt by failure mode, not enthusiasm (R6): find the pattern via the
   Failure line in `references/`, not the name.
2. Baseline-tier IDs are defaults in their domains; omitting one needs
   an ADR saying why the failure mode cannot occur.
3. Field-series (P) adoption records the observed trigger in the
   repo's ADR before the construct lands.
4. Frontier-series (X) is pilot-only: one bounded pilot, one ADR, no
   estate repo depends on an X-pattern without a second successful pilot.
5. Maturity stamps (`Proven`, `Emerging`, `Speculative`) are estate
   judgments as of 2026-11; primary sources are cited in `references/`
   where a claim is load-bearing.

## 6. Task routing graph

Pattern selection is a traversal, not a judgment call: classify the
task into a node, take its MANDATORY set, walk its ASK predicates,
obey its REFUSE edges. Full algorithm and edges:
`references/decision-graph.md`.

| Node | Task | MANDATORY |
|---|---|---|
| N01 | Paginated collection API | P7 |
| N02 | Mutating write endpoint | T1, T33, P42, P47 |
| N03 | Money movement or split | T27, P11, P12 |
| N04 | Multi-service workflow | T31, T32, T19 |
| N05 | Agent tool call / LLM output | T48, T50, P33, P37 |
| N06 | Cache layer | P21 |
| N07 | Outbound HTTP client | P24, T33 |
| N08 | Multi-tenant worker pool | P22, P23, P42 |
| N09 | Scheduler / recurrence | P8 |
| N10 | Authz / tenant data access | T8, P41 |
| N11 | Telemetry setup | P42, P45 |
| N12 | Config / feature flags | P47, P44 |
| N13 | Schema migration / rewrite | P6 |
| N14 | Client state / optimistic UI | T43, P5 |
| N15 | Numerical kernel / backtest | P12, P13, P14, P15 |
| N16 | Replicated / distributed state | T33, T34, T38 |
| N17 | New repo / module skeleton | T13, T11, P48 + §3 baseline |
| N18 | Rate limiting / load control | T35, P27 |
| N19 | Inbound webhook receiver | P54 |
| N20 | Backfill / bulk data job | P56 |
| N21 | Risky release / rewrite | P58 |
| N22 | Test suite design | P64, P68 |
| N23 | API surface design | P72 |
| N24 | Deploy / release a service | P79 |
| N25 | PII store / processing | P4, P43 |
| N26 | Trading execution | P17, P20, P92 |
| N27 | Secrets & identity | P84, P85 |
| N28 | Degraded-mode / fail-operational design | P93 |
| N29 | Release rehearsal | P98 |
| N30 | Outbound calls & time budgets | P103 |
| N31 | Dataset publishing | P110 |

Two nodes apply to one task: union the MANDATORY sets and answer both
ASK chains. Unknown ASK predicate: ask the user; never guess.

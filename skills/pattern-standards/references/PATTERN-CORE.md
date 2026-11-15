# PATTERN-CORE; the WyattAu design-pattern canon

Status: CURRENT, 2026-11. 107 patterns in three series, 8 named
refusals, a 24-pattern baseline tier. Projection source for the future
`estate-patterns` skill; consumable directly with `references/`.

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

## 2. Series and reading order

| Series | Range | File(s) | Stance |
|---|---|---|---|
| Foundations (T) | T1–T50 | `references/foundations-*.md` | Proven structural primitives; adopt by default where the domain applies |
| Field constructs (P) | P1–P50 | `references/field-*.md` | Problem-driven; adopt when the named failure mode exists |
| Frontier (X) | X1–X7 | `references/frontier.md` | Research-grade; pilot with ADR only |

Field-series domains: `field-fullstack.md` (P1–P10), `field-numerical.md`
(P11–P20), `field-concurrency.md` (P21–P30), `field-agentic.md`
(P31–P40), `field-security.md` (P41–P50). Foundations domains:
types/algebra (T1–T10), execution/reactive (T11–T20), state/time
(T21–T30), distributed (T31–T42), interfaces/security/AI (T43–T50).

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

## 6. Catalog; Foundations (T1–T50)

| ID | Pattern | Eliminates | Maturity |
|---|---|---|---|
| T1 | Parse, don't validate | defensive re-checking | Proven |
| T2 | Typestate machines | illegal transitions | Proven |
| T3 | Tagless final | expression problem | Proven |
| T4 | Free monads | welded effects | Proven |
| T5 | Functional optics | deep-update rituals | Proven |
| T6 | Higher-kinded data | DTO duplication | Proven |
| T7 | Session types | protocol desync | Emerging |
| T8 | OCap attenuation | ambient authority | Proven |
| T9 | Defunctionalization | unserializable control flow | Proven |
| T10 | Algebraic effects | bespoke effect mechanisms | Proven |
| T11 | Structured concurrency | orphaned tasks | Proven |
| T12 | Actor supervision trees | zombie partial failure | Proven |
| T13 | Functional core, imperative shell | mock-heavy tests | Proven |
| T14 | STM | uncomposable locks | Proven |
| T15 | Glitch-free signal DAGs | torn reactive state | Proven |
| T16 | Backpressure streams | consumer OOM | Proven |
| T17 | Incremental query graphs (Salsa) | full recomputation | Proven |
| T18 | Differential dataflow | batch recomputation | Proven |
| T19 | Durable replayable coroutines | lost orchestration state | Proven |
| T20 | Single-writer ring buffer | lock contention | Proven |
| T21 | Event sourcing | destroyed history | Proven |
| T22 | CQRS | one-schema conflicts | Proven |
| T23 | CRDTs | coordination locks | Proven |
| T24 | Fractional indexing | reorder races | Proven |
| T25 | Local-first sync engines | network-dead apps | Proven |
| T26 | Bitemporal modeling | destroyed beliefs | Proven |
| T27 | Double-entry immutable ledger | drifting balances | Proven |
| T28 | Content-addressed Merkle DAGs | path identity | Proven |
| T29 | Persistent sharing / MVCC snapshots | reader-writer tearing | Proven |
| T30 | E-graphs | phase ordering | Proven |
| T31 | Sagas with compensation | 2PC locks | Proven |
| T32 | Outbox + CDC | dual-write split-brain | Proven |
| T33 | Idempotency barriers | double-apply | Proven |
| T34 | Monotonic fencing tokens | zombie writes | Proven |
| T35 | Adaptive concurrency limits | static rate limits | Proven |
| T36 | Deterministic simulation testing | unreproducible races | Proven |
| T37 | Gossip dissemination | metadata bottlenecks | Proven |
| T38 | Vector clocks | lost read-your-writes | Proven |
| T39 | Hedged requests | straggler p99 | Proven |
| T40 | Zero-copy wire framing | deserialization cost | Proven |
| T41 | Bounded consistent hashing | resize storms, hotspots | Proven |
| T42 | Shuffle sharding | shared blast radius | Proven |
| T43 | Declarative reconciliation | DOM sync spaghetti | Proven |
| T44 | Resumable closure serialization | hydration cost | Proven |
| T45 | HATEOAS transitions | client-owned state machines | Proven |
| T46 | Fixed-point Datalog | unauditable authz | Proven |
| T47 | Prove-then-verify (ZK) | re-execution to trust | Emerging |
| T48 | Grammar-constrained decoding | malformed LLM output | Proven |
| T49 | Generator + verifier loops | trusted plausible output | Proven |
| T50 | Agentic capability sandboxes | agent write incidents | Proven |

## 7. Catalog; Field constructs (P1–P50)

| ID | Pattern | Eliminates | Maturity |
|---|---|---|---|
| P1 | Bi-directional version lenses | version-branched backends | Emerging |
| P2 | Isomorphic constraint capsules | validation drift | Emerging |
| P3 | Component query-plan hoisting | N+1 waterfalls | Emerging |
| P4 | `Sensitive<T>` redaction | PII/key leakage | Proven |
| P5 | Generation-tagged patches | stale-write races | Proven |
| P6 | Shadow-write parity gates | migration corruption | Proven |
| P7 | Frozen-snapshot cursors | pagination skips/dupes | Proven |
| P8 | Dual-frame temporal anchors | DST-rule breakage | Proven |
| P9 | Thin-ping pull webhooks | webhook corruption | Proven |
| P10 | Zipper wizard continuations | abandoned-branch state | Emerging |
| P11 | Remainder-preserving partition | lost/created pennies | Proven |
| P12 | Dimensional algebra | unit-mixing bugs | Proven |
| P13 | Causal horizon guards | lookahead bias | Proven |
| P14 | Fixed-topology reductions | FP non-determinism | Proven |
| P15 | `Finite<T>` NaN traps | silent NaN origin loss | Proven |
| P16 | Half-life validated quotes | stale-quote trading | Emerging |
| P17 | Risk-budget capabilities | aggregate limit breaches | Emerging |
| P18 | Distribution canaries | silent feed drift | Emerging |
| P19 | Homomorphic ledger checksums | full-scan reconciliation | Emerging |
| P20 | Unified replay clocks | live/backtest divergence | Proven |
| P21 | Caller-declared staleness | global TTL trade-offs | Proven |
| P22 | Weighted DRR pools | noisy-tenant starvation | Proven |
| P23 | `AbortScope` guards | listener leaks | Proven |
| P24 | Success-refilled retry budgets | retry amplification | Proven |
| P25 | Request-scoped arenas | GC tail latency | Proven |
| P26 | Canonical-rank lock bundles | dynamic-multi-lock deadlock | Proven |
| P27 | Propagated criticality shedding | equal-probability drops | Proven |
| P28 | Heap-snapshot forking | cold-start spikes | Proven |
| P29 | `Faulty<IO>` wrappers | untested fault paths | Proven |
| P30 | In-memory flight recorders | logging blind spots | Proven |
| P31 | Prompt quarantine | prompt injection | Proven |
| P32 | Entropy-thresholded cascades | frontier-model burn | Emerging |
| P33 | State-hash loop breakers | agent doom loops | Proven |
| P34 | Metamorphic eval gates | silent prompt drift | Emerging |
| P35 | Prefix-pinned KV layouts | cache-busting prompts | Proven |
| P36 | CoW diff envelopes | irreversible agent damage | Emerging |
| P37 | Minimal-edit repair parsers | syntax retry waste | Proven |
| P38 | Symbolic-vector cache split | near-duplicate cache hits | Emerging |
| P39 | Inference memoization | replayed pipeline cost | Proven |
| P40 | Spend-lease macaroons | runaway agent bills | Emerging |
| P41 | Tenant RLS scopes | IDOR | Proven |
| P42 | Wide-event accumulators | uncorrelatable log noise | Proven |
| P43 | Per-entity DEK shredding | undeletable PII | Proven |
| P44 | TTL-enforced flag pruning | flag archaeology | Proven |
| P45 | Burn-rate SLO gates | static-alert fatigue | Proven |
| P46 | Dependency capability manifests | transitive-dep authority | Emerging |
| P47 | Epoch-pinned config | torn config reads | Proven |
| P48 | Layering fitness gates | boundary erosion | Proven |
| P49 | Impact test fingerprinting | O(N) CI suites | Emerging |
| P50 | Hermetic synthetic twins | mock-vs-prod skew | Emerging |

## 8. Catalog; Frontier (X1–X7)

| ID | Pattern | Eliminates | Stance |
|---|---|---|---|
| X1 | Epistemic types + collapse boundaries | scattered magic thresholds | Pilot |
| X2 | Choreographic tier-splitting | full-stack glue boilerplate | Watch |
| X3 | Additive constraint manifolds | order-dependent rule trees | Pilot |
| X4 | Specification-as-source | hand-implementation as truth | Watch |
| X5 | Gauge-symmetric domain operators | conservation-breaking mutations | Pilot |
| X6 | Anytime optimal stopping | brittle timeouts | Pilot |
| X7 | Morphism-driven refactoring | speculative abstractions | Doctrine |

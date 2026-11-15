# Catalog: the full ID enumeration

The authoritative ID catalog with maturity stamps, mirroring the
`###` headings in `references/`. PATTERN-CORE stays doctrine; this
file is the lookup table. Updated together with the reference files
(AGENTS.md rule 5: referenced IDs must resolve).

## 1. Catalog; Foundations (T1–T50)

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

## 2. Catalog; Field constructs (P1–P50)

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
| P51 | Circuit breaker | cascading outage burn | Proven |
| P52 | Bulkhead isolation | shared-pool starvation | Proven |
| P53 | Dead-letter quarantine | poison-message blocking | Proven |
| P54 | Webhook receiver hardening | forged/replayed deliveries | Proven |
| P55 | Optimistic concurrency | lost updates | Proven |
| P56 | Checkpointed backfill | restart-amplified backfills | Proven |
| P57 | Consumer contract tests | silent provider breakage | Proven |
| P58 | Strangler fig migration | big-bang rewrites | Proven |
| P59 | Anti-corruption layer | legacy model leakage | Proven |
| P60 | Time-ordered identifiers | index-hostile IDs | Proven |
| P61 | Bucketed rollups + retention | raw-scan dashboards | Proven |
| P62 | Graceful drain | dropped in-flight work | Proven |
| P63 | Trace-context propagation | uncorrelatable traces | Proven |
| P64 | Property-based testing | imagined-input blind spots | Proven |
| P65 | Golden-master approval tests | undocumented legacy behavior | Proven |
| P66 | Mutation testing | weak assertions at high coverage | Proven |
| P67 | Structure-aware fuzzing | parser crashes on hostile input | Proven |
| P68 | Test-data builders | fixture rot, shared mutable tests | Proven |
| P69 | Flaky quarantine + bisection | CI signal rot | Emerging |
| P70 | Tolerant reader | provider-adds-field breakage | Proven |
| P71 | Schema registry + compat rules | schema evolution by hope | Proven |
| P72 | Uniform error envelope | per-endpoint error archaeology | Proven |
| P73 | Explicit list contract | injection-prone, unstable lists | Proven |
| P74 | Deprecation protocol | surprise removals, eternal rot | Proven |
| P75 | Canary + automated analysis | all-at-once bad releases | Proven |
| P76 | Blue-green instant revert | slow rollback | Proven |
| P77 | Shadow traffic | first-real-input rewrites | Proven |
| P78 | Progressive exposure cohorts | flag-flip casualties | Proven |
| P79 | Content-addressed artifacts | rebuild-and-pray deploys | Proven |
| P80 | Consent state machine | unanswerable consent queries | Proven |
| P81 | DSAR export pipeline | archaeology-per-request | Proven |
| P82 | Purpose-limitation tagging | invisible purpose creep | Emerging |
| P83 | Hash-chained audit log | editable audit history | Proven |
| P84 | Workload identity | shared static secrets | Proven |
| P85 | Zero-downtime rotation | deferred rotations | Proven |
| P86 | Break-glass access | standing admin creds | Proven |
| P87 | Order slicing (TWAP/VWAP) | single-clip market impact | Proven |
| P88 | Smart order routing | worse-than-available fills | Proven |
| P89 | Fill reconciliation | month-end break discovery | Proven |
| P90 | Slippage benchmarking (TCA) | hidden execution cost | Proven |
| P91 | Data-budget adaptation | burst disconnects | Proven |
| P92 | Kill switch | unstoppable rogue orders | Proven |
| P93 | Fail-operational degraded modes | function death with component death | Proven |
| P94 | Watchdog + heartbeat supervision | wedged-but-alive processes | Proven |
| P95 | 2oo3 voting | undetectable single-channel lies | Proven |
| P96 | Verify-every-layer | stage-boundary shape drift | Proven |
| P97 | Auto-blessing golden masters | golden-suite rot | Proven |
| P98 | Dress-rehearsal release gate | first-real-sequence-in-prod | Proven |
| P99 | Structural coverage gates (MC/DC) | untested decision combinations | Proven |
| P100 | Margin budgets | resources at 100% with no reserve | Proven |
| P101 | Scheduled chaos experiments | untested production failure paths | Proven |
| P102 | Ontology + lineage | table soup, impact archaeology | Proven |

## 3. Catalog; Frontier (X1–X7)

| ID | Pattern | Eliminates | Stance |
|---|---|---|---|
| X1 | Epistemic types + collapse boundaries | scattered magic thresholds | Pilot |
| X2 | Choreographic tier-splitting | full-stack glue boilerplate | Watch |
| X3 | Additive constraint manifolds | order-dependent rule trees | Pilot |
| X4 | Specification-as-source | hand-implementation as truth | Watch |
| X5 | Gauge-symmetric domain operators | conservation-breaking mutations | Pilot |
| X6 | Anytime optimal stopping | brittle timeouts | Pilot |
| X7 | Morphism-driven refactoring | speculative abstractions | Doctrine |


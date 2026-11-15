# Foundations II; Concurrency, Execution & Reactive Dataflow (T11–T20)

Replacing locks, callbacks, and naive Observer trees with deterministic
scheduling and dependency DAGs.

### T11 · Structured concurrency
**Failure.** Detached tasks outlive their logical scope; errors vanish, shutdown leaks, cancellation is a guessing game.
**Mechanism.** A lexical nursery: child tasks cannot outlive the block; parent waits for all, cancels all on first failure, and propagates one error.
**Analysis.** Proven (Python trio/anyio, Kotlin coroutines, Swift; JDK structured concurrency in preview). Cost: restructuring fire-and-forget habits; queues replace spawns for work that must outlive the request. Refuse nowhere; this is baseline-tier estate policy for all new concurrent code.
**Links.** P23 (AbortScope) is the subscription-shaped version; T12 composes supervision with it.

### T12 · Actor supervision trees ("let it crash")
**Failure.** Scattered `try/catch` around partial failure produces zombie states; half-updated caches, wedged connections.
**Mechanism.** State lives in share-nothing actors; supervisors own restart policy (one-for-one, rest-for-one) and reset children to a known-good state on crash.
**Analysis.** Proven (Erlang/OTP since the 1980s, Elixir, Akka). Cost: mailbox model friction with request/response habits; debugging moves to message traces. Refuse in single-node request handlers where a request-scoped error boundary (T11) is simpler.
**Links.** T34 (fencing) covers the storage side of crashed actors; P24 (retry budgets) caps the restart amplification.

### T13 · Functional core, imperative shell
**Failure.** Unit tests mock five dependencies to test one decision; the mocks assert the implementation, not the behavior.
**Mechanism.** Push all I/O to a thin outer shell; the core is pure functions from data to decisions. Tests exercise decisions with plain inputs/outputs; no mocks.
**Analysis.** Proven (Gary Bernhardt 2012; standard in the Rust estate kits). Baseline-tier estate policy for domain logic. Refuse nowhere in new code; retrofit opportunistically.
**Links.** T4/T10 (effect interpretation) and T36 (DST) both test the shell without mocks.

### T14 · Software transactional memory (STM)
**Failure.** Hand-rolled locks around multi-variable invariants deadlock or corrupt; lock-based code does not compose.
**Mechanism.** Optimistic atomic blocks over shared state; conflict retries automatically, and composing two atomic operations yields one atomic operation.
**Analysis.** Proven in Haskell (GHC STM), Clojure; Emerging elsewhere. Cost: retry-cost unawareness under contention; IO must be excluded from transactions. Refuse in low-level latency paths (see T20); STM's retries are unbounded.
**Links.** P26 (lock bundles) is the lock-flavored fallback when STM is unavailable.

### T15 · Glitch-free reactive signal DAGs
**Failure.** Naive Observer propagation recomputes diamonds in inconsistent order; derived state briefly holds torn values (the classic "glitch").
**Mechanism.** Track dependency edges at runtime; propagate in topological order and pull only dirty subgraphs (Signals in SolidJS, S.js, Angular signals).
**Analysis.** Proven (SolidJS is the estate frontend baseline). Refuse nowhere in reactive UI; the only question is which signal library.
**Links.** T17 (Salsa) is the compile-time-scale version with persistence.

### T16 · Demand-driven backpressure streams
**Failure.** Push-based pub/sub turns a slow consumer into an OOM: the broker buffers what the consumer cannot absorb.
**Mechanism.** Consumers request N; producers send at most N and wait (Reactive Streams, Rust `Stream` + `poll_next`, Kafka consumer pull).
**Analysis.** Proven (Reactive Streams spec, Akka Streams, Rx `backpressure` operators). Refuse only for trivially small bounded events where a channel buffer suffices.
**Links.** P27 (criticality shedding) decides *which* items to drop when the budget is exceeded.

### T17 · Incremental memoized query graphs (the Salsa pattern)
**Failure.** Compilers and build pipelines recompute everything after a one-token edit; cross-file caches invalidate too coarsely.
**Mechanism.** Structure computation as memoized queries; each query records its inputs, and revision-flagged inputs recompute only the minimal dirty subgraph.
**Analysis.** Proven (rust-analyzer via salsa, Roslyn incremental pipelines). Cost: framing work as queries; resist caching at the wrong granularity. Adopt for any compiler, LSP, linter, or multi-stage pipeline in the estate (docs-pipeline is a candidate).
**Links.** T18 generalizes to distributed streams; P49 (call-graph test fingerprinting) applies the same idea to test selection.

### T18 · Differential dataflow
**Failure.** Streaming joins and iterative graph algorithms recompute from scratch per micro-batch; latencies are minutes, not microseconds.
**Mechanism.** Computations over collections as multiset deltas tagged with logical timestamps; operators update outputs incrementally, including fixed-point recursion.
**Analysis.** Proven (Materialize, Naiad; McSherry et al. 2013). Cost: steep framework learning curve; only pay it for genuinely iterative/incremental workloads. Refuse for plain ETL; a scheduler plus T17 is enough.
**Links.** T17 (single-node specialization); T30 (e-graphs share the "update by delta" instinct).

### T19 · Durable replayable coroutines (workflow-as-code)
**Failure.** Long-running orchestration loses in-flight state on deploy/crash; recovery logic duplicates business logic.
**Mechanism.** Persist a deterministic event log of external effects; on restart, replay to the exact yield point and continue weeks later (Temporal, Restate, Azure Durable Functions).
**Analysis.** Proven at scale. Baseline-tier for any multi-day or multi-service workflow in the estate. Cost: versioning determinism discipline (workflow code must be version-pinned per execution). Refuse for request/response that fits one transaction.
**Links.** T9 (the underlying mechanism); T21 (event sourcing for domain state; different axis, same instinct); P10 (zipper wizards) is the UI-shaped cousin.

### T20 · Single-writer ring buffer (LMAX Disruptor)
**Failure.** Mutex contention around a hot queue burns cores on cache-line ping-pong; tail latency spikes under load.
**Mechanism.** One writer appends into a pre-allocated, cache-line-padded ring; consumers track sequence numbers with memory barriers, no locks.
**Analysis.** Proven (LMAX, 2011; mechanical sympathy school). Cost: single-writer constraint demands an architecture where mutation is funneled; that discipline is most of the value. Adopt in latency-critical estate paths only (breaker, ingest hot loops); elsewhere T14/T11 suffice.
**Links.** P14 (deterministic reductions share the fixed-topology instinct); P25 (arenas remove the allocation side of the same problem).

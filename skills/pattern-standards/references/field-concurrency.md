# Field III; Concurrency, Latency & Systems Reliability (P21–P30)

Runtime guards for the failure modes that load, time, and memory
produce when left to developer discipline.

### P21 · Caller-declared staleness contracts
**Failure.** Global cache TTLs force one trade-off for everyone: stale bugs or DB overload.
**Mechanism.** Callers pass `maxStale` budgets: cached age within budget returns immediately; beyond it, concurrent misses coalesce into a single-flight refresh.
**Analysis.** Proven (single-flight + caller staleness budgets are standard at scale). Adopt in cachekit's API surface. Refuse for authoritative reads where no business rule permits staleness.
**Links.** P16 (the quote-specialized version); T15 (the reactive layer above the cache).

### P22 · Weighted deficit round-robin worker pools
**Failure.** One tenant's 10,000 heavy jobs starve everyone in a shared FIFO queue.
**Mechanism.** Per-tenant queues governed by deficit counters: strict fair-share quanta under contention, idle capacity borrowed when queues are empty.
**Analysis.** Proven (DRR, Shreedhar–Varghese 1995, a networking-queue standard). Adopt in crawlkit/multi-tenant estate workers. Refuse for single-tenant workloads; a FIFO is fine.
**Links.** T42 (the multi-node version); P27 (criticality overrides fairness for emergencies).

### P23 · Lexical `AbortScope` subscription guards
**Failure.** Forgotten listeners, intervals, and WS handlers leak and fire ghost callbacks in long-lived processes.
**Mechanism.** Every async subscription takes a parent `AbortScope` token; scope exit deterministically tears down the whole listener tree.
**Analysis.** Proven (AbortController DOM standard; tokio shutdown tokens; T11 nurseries). Baseline-tier for estate long-lived processes (bot-kit, clawdius daemons). Refuse nowhere; the only cost is passing one token.
**Links.** T11 (task lifetime twin); P30 (flight recorders attach per-scope).

### P24 · Success-refilled retry budgets
**Failure.** Retries during a 10% brownout multiply traffic 5×; a blip becomes a self-inflicted total outage.
**Mechanism.** Client-wide token bucket refilled *only* by successful responses; total retry amplification capped (e.g. ≤10% of good traffic); budget exhausted → fail fast.
**Analysis.** Proven (Google SRE retry doctrine; finagle retry budgets). Baseline-tier in breaker and all estate HTTP clients. Refuse nowhere for network clients.
**Links.** breaker's circuit state; T35 (server-side admission control is the other half of the contract); T33 (idempotency makes retries safe, this makes them bounded).

### P25 · Request-scoped arena allocators
**Failure.** High-throughput APIs GC-pause or malloc-fight on millions of short-lived JSON/AST objects.
**Mechanism.** Per-request scratch objects live in a thread-local bump buffer; response completion resets the offset in O(1). No per-object frees, no GC for request debris.
**Analysis.** Proven (arena allocators throughout game/HPC; the `bytes`/serde ecosystem). The Rust estate mostly sidesteps GC; adopt where profiling shows allocation in hot loops (parsers, protocol edges). Refuse in GC languages without escape-hatch control.
**Links.** T20 (pre-allocated rings pair with arenas); T40 (zero-copy framing completes the pipeline).

### P26 · Canonical-rank lock bundles
**Failure.** `transfer(A,B)` vs `transfer(B,A)` deadlock on dynamic multi-lock acquisition.
**Mechanism.** Ban sequential `lock()`; all needed mutexes go through `LockBundle::acquire([m1, m2])` which sorts by canonical rank (address/ID) before atomic acquisition.
**Analysis.** Proven (lock-ordering discipline formalized; standard in kernels). Adopt as a kit utility wherever ≥2 locks can be held. Refuse where a single lock per entity (T14 STM, T20 single-writer) removes the problem.
**Links.** T14 (STM composes what bundles serialize); T27 (ledger accounts rank by account ID; the concrete instance).

### P27 · Propagated criticality shedding
**Failure.** Under DB load, timeouts drop the checkout request and the recommendation prefetch with equal probability.
**Mechanism.** Business criticality tier (`P0_Checkout`..`P3_Prefetch`) attached at the edge, propagated in RPC/SQL metadata; overloaded queues and pools shed P3 first, P0 last.
**Analysis.** Proven (workload management in enterprise DBs; adaptive-limit platforms). Adopt in estate API gateways and DB pools. Cost: honest tiering discipline; tiers decay if everything is P0 (refusal R8 caps the vocabulary at three honest tiers).
**Links.** T35 (the limiter that enforces); T39 (hedging gated by tier); P22 (fairness within a tier).

### P28 · Pre-warmed heap snapshot forking
**Failure.** Serverless/heavy-config workers pay multi-second cold starts re-initializing JIT state and ML weights.
**Mechanism.** Initialize once at build/deploy: snapshot the live heap, then spawn request sandboxes as copy-on-write forks of the snapshot in milliseconds.
**Analysis.** Proven at hyperscale (Lambda SnapStart, Firecracker snapshots). Cost: snapshot freshness vs config drift; pin the snapshot epoch (P47). Adopt only where cold-start cost is measured and real; refuse for always-warm services.
**Links.** P47 (config epochs); P30 (record which snapshot served).

### P29 · Deterministic fault-injecting I/O wrappers (`Faulty<IO>`)
**Failure.** Code passes happy-path mocks, then corrupts state on torn writes, 30s DNS stalls, or clock jumps in production.
**Mechanism.** Wrap Network/Disk/Clock interfaces in a PRNG-seeded wrapper for CI: deterministic partial writes, reorderings, and backward clock steps inside fast local tests.
**Analysis.** Proven (T36's lightweight sibling; chaos engineering's CI-native form). Adopt in tier-A estate kits (loom covers memory races; Faulty covers I/O). Refuse for thin wrappers around managed services whose failure model you do not credibly simulate.
**Links.** T36 (full simulation testing is the deep version); T10 (effect seams make injection free).

### P30 · Always-on in-memory flight recorders
**Failure.** Verbose debug logging kills throughput; sparse logging leaves crashes unexplained.
**Mechanism.** Compact binary micro-events stream into lock-free per-thread ring buffers (zero disk I/O); the last ~100ms of exact history flushes only when an assertion or 5xx trips.
**Analysis.** Proven (tracing ring buffers, Windows ETW, eBPF history). Adopt in estate latency-critical daemons; refuse for CRUD services where structured logs (P42) already carry the context.
**Links.** P42 (wide events are the request-level complement); P23 (scope-tagged buffers).

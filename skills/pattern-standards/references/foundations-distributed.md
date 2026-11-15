# Foundations IV; Distributed Systems & Fault Physics (T31–T42)

Engineering around partial failure, clock skew, and tail latency instead
of pretending the network is a function call.

### T31 · Saga with semantic compensation
**Failure.** 2PC coordinator locks span services and partitions; the whole waits on the slowest participant.
**Mechanism.** Forward-progress state machine per step; each step declares a compensating action invoked on partial failure. Compensation is semantic (refund, release), not a DB rollback.
**Analysis.** Proven (Garcia-Molina & Salem 1987; every travel/booking system). Cost: compensation must itself be idempotent and retryable; test it (T36). Refuse when the whole flow fits one ACID transaction.
**Links.** P36 (agent tool calls should run the same saga shape against a sandbox first); T33 (idempotency underlies every step).

### T32 · Transactional outbox + CDC
**Failure.** Dual writes split-brain: DB commits, broker publish fails (or vice versa); state and events diverge forever.
**Mechanism.** Commit domain mutation and outbound event rows in one local transaction; a CDC reader (Debezium-style) publishes them exactly-once-per-row.
**Analysis.** Proven. Baseline-tier for any estate service emitting domain events. Refuse nowhere in that class; the only question is Debezium vs. a poller.
**Links.** P9 (thin-ping webhooks ride on the outbox); T19 (workflow engines replace hand-rolled outbox consumption for orchestration).

### T33 · Idempotency barriers
**Failure.** At-least-once delivery double-charges, double-ships, double-emails.
**Mechanism.** Client supplies a deterministic idempotency key; the mutation checks it atomically alongside the write (`INSERT ... ON CONFLICT DO NOTHING` on the key).
**Analysis.** Proven (Stripe, every payment API). Baseline-tier for all mutating estate endpoints with retry exposure. Cost: key-scope decisions (per-user? per-cart?) and retention of the key table.
**Links.** P9 (the pull-flavored alternative); P24 (retry budgets assume idempotency exists downstream).

### T34 · Monotonic fencing tokens
**Failure.** A GC-paused or partitioned leader wakes up and writes stale state over the new leader's writes.
**Mechanism.** Storage grants a monotonic epoch on lock/lease grant; writes must carry the token and storage rejects writes with stale epochs.
**Analysis.** Proven (Chubby, ZooKeeper, Kleppmann's taxonomy). Cost: storage layer must enforce the check; Postgres advisory locks + epoch columns, etcd. Refuse for single-writer systems where the failure cannot occur.
**Links.** P7 (epoch tuples inside cursors); T12 (crashed actors rejoin through fencing).

### T35 · Adaptive concurrency limits
**Failure.** Static rate limits are wrong twice: too loose at the edge of collapse, too strict in the healthy regime.
**Mechanism.** Concurrency limit as a control loop: gradient of RTT against the minimal-latency operating point (Vegas-style AIMD, Netflix concurrency-limits) adjusts the limit continuously.
**Analysis.** Proven (Netflix adaptive limits, TCP Vegas lineage). Cost: telemetry loop must be trustworthy; cold-start needs a grace policy. Refuse for strictly capacity-bound resources (DB connections) where a fixed pool is the truth.
**Links.** P27 (criticality decides *who* is shed); P24 (retry budgets stop clients from fighting the limiter).

### T36 · Deterministic simulation testing (DST)
**Failure.** Race conditions and partial failure reproduce only in production; "worked in CI" means the CI never injected the fault.
**Mechanism.** Abstract clock, PRNG, network, and disk behind one seeded scheduler; a single seed deterministically replays years of simulated faults, partitions, and reorderings (FoundationDB's simulator, Antithesis, madsim).
**Analysis.** Proven (FoundationDB, TigerBeetle, TigerStyle). Cost: the I/O abstraction boundary; pay it once per kit. Baseline-tier for estate concurrency primitives (tier-A repos already run loom; DST extends that to protocols). Refuse for thin CRUD wrappers.
**Links.** P29 (Faulty<IO> is the lightweight CI-shaped version); T10 (effects make the seams free).

### T37 · Epidemic / gossip dissemination
**Failure.** Central coordinator for cluster metadata is a bottleneck and a domain of failure at N>1000 nodes.
**Mechanism.** Nodes exchange state deltas with random peers; updates spread in O(log N) rounds (SWIM, Plumtree).
**Analysis.** Proven (SWIM in Hashicorp stack, Cassandra, Bitcoin's ad-hoc gossip). Refuse below a few hundred nodes or where a control plane (etcd/Headscale) is already present and sized.
**Links.** T38 (causal metadata rides along in gossip state).

### T38 · Causal consistency via logical / vector clocks
**Failure.** Eventually consistent replicas violate read-your-writes; clients see their own updates vanish.
**Mechanism.** Ship causal-frontier tokens (vector clocks / hybrid-logical clocks) with writes; replicas and clients gate reads on the frontier so causality holds without global coordination.
**Analysis.** Proven (Dynamo lineage, COPS, YugabyteDB). Cost: clock-token plumbing and conflict-resolution semantics. Refuse where a single logical shard provides the ordering for free.
**Links.** P5 (generation tags are the client-session version); T26 (bitemporal storage of the causally-stamped facts).

### T39 · Hedged requests
**Failure.** p99 is owned by stragglers: one slow replica of three defines the tail.
**Mechanism.** After the p95 delay, fire a duplicate request; first response wins, loser cancelled.
**Analysis.** Proven (Dean & Barroso, "The Tail at Scale", 2013). Cost: duplicate load; cap hedge ratio and exclude non-idempotent or expensive-side-effect calls. Refuse for writes; T33 exists for those.
**Links.** X6 (optimal stopping generalizes when-to-hedge into a scheduler); P27 (criticality gates who may hedge).

### T40 · Zero-copy wire framing
**Failure.** Deserialization of hot-path messages burns CPU and allocations on field-by-field copies.
**Mechanism.** Design the wire layout identical to in-memory alignment (Cap'n Proto, FlatBuffers, rkyv); parse becomes an O(1) bounds-checked cast.
**Analysis.** Proven (Cap'n Proto, rkyv in latency-sensitive Rust). Cost: schema evolution discipline; field ordering is ABI. Adopt for estate internal hot paths; JSON at the edges is fine.
**Links.** P20 (unified replay envelopes can use this for tick transport); P25 (arenas complete the zero-alloc pipeline).

### T41 · Consistent hashing with bounded loads
**Failure.** Naive mod-N sharding moves nearly every key on resize; unbounded ring hashing creates hotspots.
**Mechanism.** Hash ring plus per-node capacity cap (CHASH with loads, Google 2016): O(K/N) key movement while bounding skew.
**Analysis.** Proven (Dynamo, Memcached clients, Envoy). Refuse for N so small that an explicit assignment table is cheaper to reason about.
**Links.** T42 (shuffle sharding is the multi-tenant blast-radius complement).

### T42 · Shuffle sharding
**Failure.** One poison tenant on shared nodes degrades every co-located tenant.
**Mechanism.** Each tenant gets its own random k-of-N node subset; overlap probability between two tenants is ~1/C(N,k), so blast radius shrinks combinatorially.
**Analysis.** Proven (AWS internal, published by AWS Builders' Library). Cost: operational complexity; per-tenant routing tables and capacity math. Adopt for noisy-tenant estate services (crawlkit tiers); refuse for uniformly benign tenants.
**Links.** P22 (DRR queues are the same fairness goal inside one node).

# Foundations III; State, Time & Persistence Topologies (T21–T30)

Treating time, causality, and conservation laws as first-class structural
primitives rather than implicit side effects.

### T21 · Event sourcing
**Failure.** Mutable current-state rows destroy history; audits reconstruct guesswork, retroactive projections are impossible.
**Mechanism.** Immutable append-only log of domain transitions is the source of truth; current state is a projection that can be rebuilt at any time.
**Analysis.** Proven (CQRS community, Kafka-backed estates, banking cores). Cost: schema evolution of events, eventual-consistency read models, and event-store ops. Refuse where current state plus T26 (bitemporal columns) answers every audit question; event sourcing is powerful, not free.
**Links.** P43 (crypto-shredding solves its GDPR deletion problem); T28 (Merkle DAGs give it diffing); P6 (parity gates de-risk its migrations).

### T22 · CQRS
**Failure.** One schema serves conflicting access patterns: write-side normalization forces read-side joins that cannot scale, and vice versa.
**Mechanism.** Physically split command-side invariant enforcement from query-side denormalized projections; each side optimizes its own shape.
**Analysis.** Proven. Cost: projection lag and dual schema maintenance; pay it only where read/write shapes actually conflict. Refuse for CRUD where a table plus indexes already serves both sides.
**Links.** T21 (the natural write model); P9 (thin-ping webhooks drive projection refresh).

### T23 · CRDTs
**Failure.** Offline-capable or multi-master replicated state needs coordination locks or merges corrupt.
**Mechanism.** State as a join-semilattice: commutative, associative, idempotent merge; replicas converge without coordination (LWW-registers, PN-counters, RGA/sequence CRDTs).
**Analysis.** Proven (Figma, Automerge/Yjs, Riak, Redis). Cost: semilattice design is subtle; interleaving-attack and convergence anomalies are literature-deep; use a library, not a hand-rolled merge. Refuse when a single-writer shard (T20) is available.
**Links.** T25 (local-first engines package CRDTs with sync); T24 (fractional indexing) supplies the ordering keys.

### T24 · Fractional indexing
**Failure.** Reordering N list items rewrites N rows and races with concurrent reorderers.
**Mechanism.** Lexicographic dense keys between neighbors (`a0`, `a0g`, …); reorder mutates one row's key; rebalancing is a rare background job.
**Analysis.** Proven (Figma's fractional indexing, Jitter/Linear-style implementations). Cost: key-length growth until rebalance; use a vetted library for midpoint precision. Refuse for write-once ordered data; plain integer positions are simpler.
**Links.** P10 (zipper wizards reuse the ordering discipline); T23 provides the concurrent-reorder safety net.

### T25 · Local-first sync engines
**Failure.** Web apps dead on bad networks; server round-trips for every keystroke; optimistic UI code ad-hoc everywhere.
**Mechanism.** Embedded client DB is primary; mutations apply locally and queue; background delta reconciliation with server (Automerge, ElectricSQL, PowerSync, Replicache).
**Analysis.** Proven (Ink & Switch "Local-first software", 2019; production sync engines since). Cost: conflict semantics must match domain needs; pick the engine by merge behavior, not benchmarks. Refuse for server-authoritative flows (payments, admin).
**Links.** P5 (generation-tagged patches is the manual optimistic-UI primitive this replaces); T23 underneath.

### T26 · Bitemporal modeling
**Failure.** Retroactive corrections overwrite reality: you can never answer "what did we believe on March 3?" after a restatement.
**Mechanism.** Two time axes per fact: valid time (when true in reality) and transaction time (when the system believed it); corrections append, never update.
**Analysis.** Proven (SQL:2011 system-versioned tables, Marklogic, quant data vendors). Cost: query complexity doubles at the corners; index both axes. Adopt wherever restatements are real: accounting-spec, cal-model, positions data. Refuse for ephemeral UI state.
**Links.** P13 (as-of guards enforce the query-side discipline); T21 is the append-only cousin at event granularity.

### T27 · Double-entry immutable ledger
**Failure.** `balance` columns drift under races and bugs; no structural way to prove conservation.
**Mechanism.** Paired append-only entries where every mutation nets to zero (`Σ debits + Σ credits = 0`); balances are derived sums, never stored as authority.
**Analysis.** Proven (500 years of accounting; TigerBeetle as the modern engineered form). Baseline-tier for anything moving value in the estate; accounting-spec (X4 Lean model is the truth source). billing-kit is value-adjacent only (T27 n/a: decimal arithmetic, no ledger surface; drift-check caught the association, 2026-11-20). Refuse nowhere for value; extend to inventory/quota via P17-style tokens. (accounting-spec: adopted); (billing-kit: n/a)
**Links.** P11 (remainder-preserving partition allocates the entries); X5 (gauge-symmetric operators generalize conservation to any conserved quantity).

### T28 · Content-addressed Merkle DAGs
**Failure.** Identity by path/URL breaks on moves; tampering is undetectable; diffing trees is O(N).
**Mechanism.** Address data by `hash(contents)`; containers reference children by hash; structural sharing, tamper evidence, O(log N) diffs fall out.
**Analysis.** Proven (Git, IPFS, Bittorrent v2, cas-kit in the estate). Refuse nowhere for artifacts; refuse for mutable small records where hash overhead buys nothing.
**Links.** P39 (inference memoization keys on this); P19 (homomorphic checksums for reconciliation); P49 (test fingerprints).

### T29 · Persistent structural sharing / MVCC snapshots
**Failure.** Readers block writers or read torn state; snapshot isolation is reimplemented badly per app.
**Mechanism.** Copy-on-write persistent trees: a reader pins a root pointer and sees an immutable point-in-time view; writers clone only the spine they touch.
**Analysis.** Proven (Postgres MVCC, Git, immutable.js, im-rs). Refuse nowhere at the DB level; the pattern is for application-level in-memory snapshots of large shared state (config, caches).
**Links.** P47 (epoch-pinned config is the request-scoped version); P7 (frozen cursors exploit MVCC for pagination).

### T30 · E-graphs (equality saturation)
**Failure.** Rewrite passes are order-dependent: phase A destroys the shape phase B needed; optimizers plateau at local minima.
**Mechanism.** Store all equivalent forms simultaneously in an equivalence graph; saturate with rewrites, then extract the best representative once (egg, Relational Algebra optimizers).
**Analysis.** Proven (egg, Skewed compiler work, SQL engines exploring join orders). Cost: matching/analysis engineering; blowup control needs pruning. Adopt inside optimizers and refactoring tools; refuse as a runtime component.
**Links.** X7 (morphism-driven refactoring is the application-code cousin); X3 (constraint manifolds share the "settle globally" instinct).

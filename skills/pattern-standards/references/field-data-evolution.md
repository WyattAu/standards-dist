# Field VII: Data Integrity & Evolution (P55–P61)

Constructs for concurrent writers, bulk data work, and safe long-term
change. All Proven; most failures here are silent until they are
expensive.

### P55 · Optimistic concurrency control
**Failure.** Two writers read-modify-write the same row; the second clobbers the first. Lost updates are invisible: no error, just wrong data.
**Mechanism.** Version column or ETag on every contended entity; writes carry the expected version (`If-Match` or `WHERE version = ?` compare-and-swap); mismatch returns 409/412 and the client re-reads and reapplies its intent, not its stale bytes.
**Analysis.** Proven (HTTP `If-Match`, JPA `@Version`, Postgres `xmin` tricks). Adopt for any entity two actors can edit; especially config-like rows and documents. Refuse for write-once data and for hot counters (atomic increments beat OCC there).
**Links.** T33 (replay safety; OCC is concurrent-writer safety), T29 (snapshot reads feed the retry), P47 (config rows are the classic case).

### P56 · Checkpointed backfill
**Failure.** A multi-hour backfill dies at 90%; the restart re-does everything, double-applies non-idempotent steps, or hammers the primary into lag.
**Mechanism.** Unit of work = one idempotent transform keyed by PK range or token; a checkpoint table records completed ranges; fixed batch size with pacing; restart resumes from the checkpoint; completion is verified by a count or checksum pass.
**Analysis.** Proven (standard operations doctrine). Refuse nowhere for bulk data work; a backfill without a checkpoint is a bet against reality.
**Links.** T33 (each unit idempotent), P6 (parity pass after), P19 (checksum verification), P22 (pacing so tenants are not starved).

### P57 · Consumer-driven contract testing
**Failure.** A provider changes a field or a semantic; consumers break in production because provider-side unit tests never modeled them.
**Mechanism.** Consumers publish machine-readable expectations (pacts); provider CI verifies the implementation against every consumer contract before merge; a breaking change fails the provider's build, not the consumer's runtime.
**Analysis.** Proven (the pact ecosystem and descendants). Adopt wherever provider and consumer deploy independently. Refuse inside one monorepo where shared schema codegen (T6) already binds both sides at compile time.
**Links.** P1 (lenses make compatible evolution explicit), T7 (formal protocol types are the compile-time version of the same guarantee).

### P58 · Strangler fig migration
**Failure.** A risky system rewrite attempts a big-bang cutover, runs over budget, and reverts after months of parallel darkness.
**Mechanism.** Intercept traffic at one seam (edge route or facade); move route by route onto the new implementation; each slice ships with its own rollback; the old system is the last thing to die, not the first.
**Analysis.** Proven (Fowler, 2004; the dominant rewrite doctrine). Refuse for rewrites with no traffic seam to intercept; if you cannot strangle, you cannot safely rewrite.
**Links.** P59 (the translation seam), P6 (parity evidence per slice), P44 (routing flags carry expiries).

### P59 · Anti-corruption layer
**Failure.** A legacy or vendor model leaks into the new domain: nullable legacy flags, status enums with vendor values, and soon the new code speaks the old system's dialect.
**Mechanism.** One boundary adapter translates foreign models into the domain's own types; the domain compiles without the foreign schema on its classpath; foreign changes stop at the adapter.
**Analysis.** Proven (Evans, "Domain-Driven Design", 2003). Adopt at every integration with a model you do not own. Refuse for greenfield integrations where you design the shared contract directly.
**Links.** T1 (parsing the legacy payload into domain types is the adapter's core), P58 (the strangler's seam is usually an ACL), P1 (ongoing compatibility lenses).

### P60 · Time-ordered identifiers
**Failure.** Autoincrement IDs leak volume and collide across shards; random UUIDs shred index locality and cannot be sorted by creation.
**Mechanism.** Time-prefixed random IDs (UUIDv7 or ULID shape): globally unique, roughly sortable, b-tree friendly. Creation order is recoverable from the ID without a sequence bottleneck.
**Analysis.** Proven (RFC 9562 UUIDv7, 2024; ULID lineage). Baseline for new distributed tables. Refuse when identifiers must be unguessable and carry no order: random UUIDv4 plus an explicit sort key.
**Links.** T24 (list ordering is a separate concern from identity), T28 (content addressing for content; identity IDs for entities), T38 (IDs are not causal tokens).

### P61 · Bucketed rollups + tiered retention
**Failure.** Dashboards scan raw event tables (seconds of latency, Terabytes of scan); forever-retention balloons storage and legal exposure simultaneously.
**Mechanism.** Pre-aggregate into fixed time buckets (1m/1h/1d) with idempotent upserts; retention tiers: raw short, rollups long; every query targets the coarsest tier that answers it. Bucket writes survive replay (P56-style idempotency).
**Analysis.** Proven (time-series DB practice; continuous aggregates). Adopt for any append-heavy event stream with aggregate consumers. Refuse for small datasets where the raw table answers everything in milliseconds.
**Links.** T21 (raw retention policy rides the event log), P56 (backfills recompute buckets idempotently), P42 (wide events feed the buckets).

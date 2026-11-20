# Field I; Full-Stack, UI & Schema Evolution (P1–P10)

Problem-driven constructs where the trigger is a concrete failure mode.
Adopt only when the failure mode is present (refusal R6). Cross-links
to the T-series foundations appear per pattern.

### P1 · Bi-directional version lenses
**Failure.** Supporting v1/v2/v3 API clients forks controllers and sprinkles `if version` branches through the backend.
**Mechanism.** Write logic once against `v_latest`; declare only adjacent lenses (`v1↔v2`, `v2↔v3`) at the edge: inbound upgrades forward, outbound projects backward. Lenses compose; non-adjacent clients transit the chain.
**Analysis.** Emerging (lens pipelines in payment APIs). Cost: lens tests per hop, deprecation ledger. Adopt when >2 client generations must coexist; refuse when all clients upgrade in lockstep (internal estate tools).
**Links.** P6 (parity gates verify lens round-trips); T6 (HKD generates lens boilerplate).

### P2 · Isomorphic constraint capsules
**Failure.** Client form validation, server validation, and DB constraints drift; UX rejects what the DB accepts and vice versa.
**Mechanism.** Compile pure domain predicates once into a deterministic artifact (WASM/bytecode/SQL-function codegen) executed identically in browser, backend, and trigger.
**Analysis.** Emerging (schema-first codegen is the pragmatic 80%: JSON Schema → zod + SQL CHECK). Full capsule parity is rarely worth the toolchain; the invariant to keep is single-source predicates. Refuse when constraints are trivially declarative in each layer.
**Links.** T1 (parse with these predicates); P48-style CI gates verify capsule freshness.

### P3 · Static component query-plan hoisting
**Failure.** Leaf components' data needs surface at runtime as N+1 waterfalls or fragile mega-resolvers.
**Mechanism.** Build-time AST pass extracts each route's leaf data requirements and compiles one prepared SQL/RPC join per route; components receive data by position, not by fetching.
**Analysis.** Emerging (the Relay compiler proved the model; framework-integrated variants since). Cost: compiler coupling to component idioms. Adopt for large route trees with deep component data needs; refuse for small apps where a loader-per-route convention suffices.
**Links.** T17 (the same "hoist to one prepared query" instinct at pipeline scale).

### P4 · Taint-tracked redaction (`Sensitive<T, Policy>`)
**Failure.** PII, keys, tokens leak into logs, Sentry breadcrumbs, and LLM prompts because sanitization depends on memory.
**Mechanism.** Opaque wrapper whose `Display`/`Serialize` emits `[REDACTED]`; unwrapping requires a capability-checked sink (`logAudit(val, key)`). Taint flows through `Debug` derives and error chains.
**Analysis.** Proven in security-conscious Rust/TS codebases (secrecy crates, redacted derives). Baseline-tier for estate services touching credentials or PII (argus, auditlog). Refuse nowhere in that class; the cost is one wrapper per language.
**Links.** T8 (the sink is a capability); P31 (the LLM prompt boundary must use the same wrapper).

### P5 · Generation-tagged patch channels
**Failure.** Out-of-order autosave ACKs and slow debounces overwrite newer keystrokes in editors.
**Mechanism.** Tag mutations and server ACKs with monotonic `(docEpoch, localSeq)`; the client reducer drops any server snapshot whose epoch lags the active dirty epoch.
**Analysis.** Proven in collaborative editors (OT/CRDT systems formalize it). Adopt for any optimistic-UI mutation queue; refuse when T23/T25 (CRDT/sync engine) already sequence for you.
**Links.** T25 (sync engines subsume); T38 (the distributed generalization).

### P6 · Shadow-write parity gates
**Failure.** Schema migrations and rewrites corrupt edge-case records that tests never modeled.
**Mechanism.** Dual-write/dual-read old and new schemas under real traffic; compute row-level canonical hashes; cutover blocked until zero-diff parity holds across a full traffic cycle.
**Analysis.** Proven at companies that migrate live ledgers (standard fintech practice). Cost: dual-write code is disposable scaffolding; delete it on cutover. Adopt for any risky rewrite of billing/accounting data in the estate.
**Links.** T21 (event sourcing makes this a projection rebuild instead); P19 (homomorphic checksums as the diff oracle); db-migration doctrine.

### P7 · Frozen-snapshot cursor envelopes
**Failure.** Infinite scroll duplicates or skips rows inserted/deleted mid-scroll.
**Mechanism.** Opaque cursor carries an MVCC snapshot watermark (timestamp/LSN) plus deterministic tie-broken `(sortKey, pk)`; pages read a mathematically frozen set.
**Analysis.** Proven (Postgres `repeatable read` + keyset pagination is the composed form). Adopt for all paginated estate APIs; refuse offset pagination outright (refusal R5: offsets skip and duplicate by construction).
**Links.** T29 (the snapshot substrate); T34 (epoch discipline shape).

### P8 · Dual-frame temporal anchors
**Failure.** Future recurring events stored as UTC instants break by an hour when governments change DST rules.
**Mechanism.** Persist `(WallTime, IANA_Zone, RecurrenceRule)`; materialize concrete UTC instants lazily via current tzdata at query time. The stored fact is the civil intent, not an instant.
**Analysis.** Proven doctrine (calendar-standard advice; iCalendar RRULE + TZID shape). Baseline-tier for all future estate scheduling; no dedicated calendar crate exists yet (cal-model is A2L automotive calibration, a different domain; drift-check caught this association, 2026-11-18). Refuse for past events; record the actual instant that occurred. (cal-model: refused)
**Links.** P13 (as-of joins decide which tzdata version answered).

### P9 · Thin-ping pull webhooks
**Failure.** Out-of-order, duplicated, or dropped webhooks corrupt consumer state machines.
**Mechanism.** Webhooks carry only `{entityId, minVersion}` invalidation pings; consumers pull idempotently asserting `fetched.version >= minVersion`. Delivery semantics degrade from correctness-critical to cache-invalidation.
**Analysis.** Proven lineage (delivery-dedup hints in major webhook APIs; feed-reader pull models). Adopt for estate outbound webhooks where consumers are untrusted or flaky. Refuse for low-latency consumers that already run T32 CDC.
**Links.** T32 (outbox drives the pings); T33 (the pull is idempotent); P5 (epoch tags on the consumer side).

### P10 · Zipper-backed wizard continuations
**Failure.** Jumping backward in multi-step forms leaves contradictory downstream state from abandoned branches.
**Mechanism.** Model the workflow as a typed state zipper; moving back prunes strictly-dependent downstream subtrees and preserves orthogonal inputs.
**Analysis.** Emerging (zipper = proven structure, Huet 1997; the workflow application is newer). Cost: dependency typing per step. Adopt for long structured flows (onboarding, migration wizards); refuse for linear wizards where "back" means "clear step N".
**Links.** T19 (durable workflows persist the zipper); T9 (inspectable control flow).

# Decision graph: task-type routing (deterministic pattern selection)

Pattern selection is a traversal, not a judgment call. Classify the
task into one node, collect its M (mandatory) set, walk its A (ask)
predicates in order, obey its R (refuse) edges, emit the ID set. The
agent never weighs alternatives; the graph decides. Deviations from an
M entry need an ADR (PATTERN-CORE §5); A predicates that cannot be
answered from the task requirements go to the user as a question, not
a guess.

Deterministic traversal is scripted: `scripts/route.py --task "<task>"`
(or `--node N08`, or `--list`) parses this file and prints the block.
Use the script before reading this file; it costs one call instead of
a full read.

## Format

Each node block is four fixed lines under a `### NXX · Name` heading,
parsed by `scripts/route.py`; format drift breaks the router
(AGENTS.md rule 10):

- `K:` classification keywords for `--task` matching
- `M:` mandatory pattern IDs (baseline; omitting one needs an ADR)
- `A:` ask predicates, `predicate -> ID[, ID]`, semicolon-separated,
  walked top to bottom; an unknown predicate goes to the user
- `R:` refuse edges, semicolon-separated; a matched edge redirects or
  halts, never proceeds

## Traversal algorithm

1. Classify: map the task to exactly one node (route.py scores task
   words against K lines). Two nodes apply: union the M sets and walk
   both A chains; overlaps are consistent by design.
2. Collect: the node's M IDs are baseline, no discussion.
3. Branch: walk A predicates top to bottom; yes adds the IDs, no skips.
4. Refuse: a matched R edge redirects or halts; the refused variant
   does not proceed in any form.
5. Emit: the ID set plus the reference files those IDs live in. That
   set is the design; anything beyond it needs the failure mode to name
   a pattern outside the node (PATTERN-CORE §5 rule 1).

## Node index

| Node | Task |
|---|---|
| N01 | Paginated collection API |
| N02 | Mutating write endpoint |
| N03 | Money movement or split |
| N04 | Multi-service workflow |
| N05 | Agent tool call / LLM output |
| N06 | Cache layer |
| N07 | Outbound HTTP client |
| N08 | Multi-tenant worker pool |
| N09 | Scheduler / recurrence |
| N10 | Authz / tenant data access |
| N11 | Telemetry setup |
| N12 | Config / feature flags |
| N13 | Schema migration / rewrite |
| N14 | Client state / optimistic UI |
| N15 | Numerical kernel / backtest |
| N16 | Replicated / distributed state |
| N17 | New repo / module skeleton |
| N18 | Rate limiting / load control |
| N19 | Inbound webhook receiver |
| N20 | Backfill / bulk data job |
| N21 | Risky release / rewrite |
| N22 | Test suite design |
| N23 | API surface design |
| N24 | Deploy / release a service |
| N25 | PII store / processing |
| N26 | Trading execution |
| N27 | Secrets & identity |
| N28 | Degraded-mode / fail-operational design |
| N29 | Release rehearsal |
| N30 | Outbound calls & time budgets |
| N31 | Dataset publishing |

## Node blocks

### N01 · Paginated collection API
K: list, page, pagination, cursor, infinite scroll, collection, table
M: P7
A: multi-tenant data -> P41; infinite scroll or autosave nearby -> P5; deeply nested UI data -> P3; read-after-write consistency -> P108
R: offset pagination, replace with P7 (R5), no exception for small tables

### N02 · Mutating write endpoint
K: write, endpoint, mutation, create, update, POST, ingest
M: T1, T33, P42, P47
A: money fields -> N03; PII in payload -> P4, P43; downstream retry-exposed calls -> P24; events emitted -> T32; concurrent writers -> P55; long-running transactions -> P106
R: fire-and-forget writes that skip the outbox, route through N04's T32 or do not emit

### N03 · Money movement or split
K: money, payment, split, fee, billing, cents, ledger, charge, refund, invoice, price, metering, usage, quota
M: T27, P11, P12
A: reconciled against external ledger -> P19; restatements possible -> T26; shared account across strategies -> P17
R: floating-point money in any language; mutable balance columns as stored truth (R4); percentage math in floats

### N04 · Multi-service workflow
K: workflow, saga, orchestration, multi-service, multi-step, compensation, choreography, outbox, broker, domain events
M: T31, T32, T19
A: steps call third parties -> T33; initiated or stepped by an agent -> N05, P36; human approval gates -> P36
R: cross-service 2PC; recovery logic hand-rolled outside T19; non-idempotent compensation actions

### N05 · Agent tool call / LLM output
K: agent, LLM, tool call, prompt, model output, generation, structured output
M: T48, T50, P33, P37
A: reads untrusted text -> P31; multi-turn -> P35; multi-stage pipeline -> P39; sub-agent spawning -> P40; write access -> P36, P44
R: JSON.parse on raw model output; agent writes without an approval diff; retry loops without P33

### N06 · Cache layer
K: cache, TTL, stale, memoization, invalidate, read-through
M: P21
A: market data or quotes -> P16; semantic or vector search -> P38, P39; client-side optimistic state -> P5
R: global TTL as the only staleness policy; caching authoritative writes

### N07 · Outbound HTTP client
K: HTTP, client, outbound, fetch, third-party, API call, retry, webhook out
M: P24, T33, P51, P103
A: tail-latency-sensitive reads -> T39; business tiers -> P27; parses third-party content -> P46; shared pool across dependencies -> P52; resolver failures hurt -> P104; consumes tokens -> P114
R: unbounded exponential backoff; retries on non-idempotent endpoints without T33; bare calls with no breaker state

### N08 · Multi-tenant worker pool
K: worker, queue, pool, job, background, tenant fairness, cron in pool, dead-letter, poison
M: P22, P23, P42
A: poison-tenant blast radius -> T42; latency-critical jobs -> P30; fault paths tested -> P29; daemon wedge detection -> P94; scheduled jobs in the pool -> P105
R: one shared FIFO across tenants; detached tasks outside an AbortScope

### N09 · Scheduler / recurrence
K: schedule, cron, recurrence, calendar, timezone, DST, appointment
M: P8
A: corrections to past facts -> T26; consumed by backtests -> P13; DST-sensitive -> verify tzdata versioning query-visible
R: future recurring events stored as UTC instants

### N10 · Authz / tenant data access
K: authz, permission, tenant, RLS, access control, capability, role, delegation
M: T8, P41
A: role or delegation logic beyond booleans -> T46; conserved quantities (grants, quotas) -> X5 per ADR-0001
R: hand-written WHERE tenant_id as the only control; repositories constructed without a tenant capability

### N11 · Telemetry setup
K: telemetry, logs, metrics, alerts, tracing, observability, SLO, paging
M: P42, P45, P63
A: latency-critical daemon -> P30; PII can reach traces -> P4, P43
R: scatter-shot logger.info as primary observability; static threshold paging; logs unjoinable by one trace ID

### N12 · Config / feature flags
K: config, feature flag, settings, toggle, expiry of flags
M: P47, P44
A: forked or snapshot workers -> P28; per-request consistency -> P47 covers it, do not add a second mechanism
R: live-reloaded globals read mid-request; permanent flags that are really configuration, route to P47

### N13 · Schema migration / rewrite
K: migration, schema, rewrite, expand-contract, alter, cutover
M: P6
A: ledger or accounting data -> P19; event-sourced store -> T21 project rebuild; replacing a legacy path end to end -> N21, P58, P59
R: big-bang cutover without parity evidence; migrations without a tested rollback

### N14 · Client state / optimistic UI
K: UI, client state, optimistic, form, frontend, render, autosave
M: T43, P5
A: offline-capable -> T25, T23; long structured flows -> P10; server-owned flow -> T45; heavy nested data -> P3
R: manual DOM or listener synchronization; mirrored client state machine without T45

### N15 · Numerical kernel / backtest
K: numerical, kernel, backtest, float, NaN, quant, matrix, feature compute
M: P12, P13, P14, P15
A: live and historical paths -> P20; parallelism -> P14 is already mandatory, no ad-hoc reductions
R: naive threaded float sums; joins on calendar-date equality; NaN-tolerant pipelines

### N16 · Replicated / distributed state
K: distributed, replication, consensus, leader, shard, replicas, multi-master, partition, drift
M: T33, T34, T38
A: offline or multi-master clients -> T23 via T25; rebalancing expected -> T41; tenant isolation matters -> T42
R: dual writes, use T32; leader leases without fencing; wall-clock ordering assumptions

### N17 · New repo / module skeleton
K: repo, skeleton, new project, module, bootstrap, scaffold
M: T13, T11, P48
A: quant domain -> N15 M set; agents -> N05 M set; money -> N03 M set; compiler or multi-stage pipeline -> P96; domain data platform -> P102; capacity headroom as a requirement -> P100
R: speculative factories (R1); interface seams added for mocking (R2); layers without a fitness gate

### N18 · Rate limiting / load control
K: rate limit, load, shedding, concurrency limit, throttle, overload
M: T35, P27
A: multi-tenant fairness -> P22; client-side counterpart -> P24
R: static thresholds as the only control; criticality vocabularies where everything is P0 (R8)

### N19 · Inbound webhook receiver
K: webhook, inbound, callback, signature, delivery
M: P54
A: consumer needs current state over event order -> P9; payload feeds projections -> T32; payload feeds an agent -> P31
R: trusting sender claims without signature verification; inline processing inside the HTTP handler; mutations keyed on delivery order

### N20 · Backfill / bulk data job
K: backfill, bulk, data job, recompute, migration of rows
M: P56
A: accompanies a rewrite -> N13, P6; verifying ledger-shaped data -> P19; multi-tenant tables -> pace within P22
R: unbounded UPDATE loops with no checkpoint; backfills on hot tables without batching; non-idempotent backfill steps

### N21 · Risky release / rewrite
K: release, rewrite, strangler, legacy, cutover, migration of traffic
M: P58
A: legacy model at the boundary -> P59, P1; data parity between old and new -> P6; routing switches -> P44 expiries
R: big-bang cutover; parallel-run scaffolding with no expiry; a strangler with no traffic seam

### N22 · Test suite design
K: test, suite, coverage, flaky, property, fuzz, assertion strength
M: P64, P68
A: legacy or undocumented code -> P65; golden masters already in CI -> P97; parser or protocol edge -> P67, P29; suite suspects weak -> P66; over ~50 tests with flakes -> P69; regulated or safety-critical target -> P99; ORM list views under test -> P109
R: mock-driven suites (R2); snapshots as the only spec for new code; coverage percentages quoted as strength

### N23 · API surface design
K: API design, error shape, contract, public schema, deprecation, endpoint design
M: P72
A: list endpoints -> P73; consumers outside the deploy unit -> P70, P57, P71; long-lived external API -> P74
R: per-endpoint error shapes; silent-ignore of unknown query params; breaking removals without the P74 window; offset pagination, N01 owns it

### N24 · Deploy / release a service
K: deploy, release, canary, rollout, artifact, ship, blue-green, revert, flip, launch
M: P79
A: risky behavioral change -> P75; revert speed dominates -> P76; rewrite needs real-input validation -> P77; user-visible feature -> P78; full-sequence rehearsal -> P98, N29; capacity margin for the new version -> P100
R: artifacts not bit-identical to CI-tested ones; canaries without automated analysis; shadow traffic with ungated side effects

### N25 · PII store / processing
K: PII, privacy, personal data, GDPR, redact, delete user, subject rights
M: P4, P43
A: subject export requests in scope -> P81; consent-gated purposes -> P80, P82; audit requirements -> P83; analytics feeds on PII-bearing tables -> P82; publishing derived datasets -> N31
R: untagged PII reaching analytics or training; manual queries as the DSAR answer; plaintext PII in append-only stores without a DEK

### N26 · Trading execution
K: trading, order, execution, venue, fill, broker, position
M: P17, P20, P92
A: parent orders large vs venue liquidity -> P87; multi-venue -> P88; broker on the other side -> P89, P90; venue data feeds -> P91; feed handler wedge protection -> P94
R: order paths without a halt check, N26 does not exist without P92; single-clip parent orders on thin venues; positions adjusted from unreconciled fills

### N27 · Secrets & identity
K: secrets, identity, credential, key rotation, mTLS, vault
M: P84, P85
A: incident access needed -> P86, retire any standing admin credential it replaces; external static secrets remain -> vault with audit; audit-chain requirements -> P83
R: shared static secrets in environment variables (R4 adjacent); credentials without a rotation path; admin access without expiry or audit

### N28 · Degraded-mode / fail-operational design
K: degraded, fail-operational, partial outage, watchdog, voting, shed, dies, serving, degrade
M: P93
A: hung-component detection -> P94; sensor or input redundancy -> P95; capacity headroom accounting -> P100; production validation of degradation paths -> P101
R: degradation tiers without tested exit criteria; shed lists that grow unbounded; fail-safe designs for functions that must keep serving

### N29 · Release rehearsal
K: rehearsal, dress rehearsal, test like you fly, game day, pre-release run, rehearse, launch, sequence
M: P98
A: continuous rehearsal on real traffic -> P77; replay of historical sequences -> P20, T36; production fault drill -> P101; degraded-tier rehearsal -> P93
R: rehearsal on toy or sanitized data (P50's failure mode); gates looser than release gates; happy-path-only rehearsals

### N30 · Outbound calls & time budgets
K: timeout, deadline, hang, call budget, propagation, stalled call
M: P103
A: resolver resilience -> P104; token-consuming client -> P114; scheduled or cron-shaped work -> P105; database sessions in the path -> P106
R: outbound calls without explicit timeouts; retrying past the caller's deadline; fire-and-forget work inheriting a dead caller's budget

### N31 · Dataset publishing
K: dataset, publish, expectation, freshness, data contract, table release
M: P110
A: publishing from streams or outboxes -> T32; scheduled compute behind the dataset -> P105, P56; feeding models -> P111; PII-bearing datasets -> P4, P43, N25; cost-heavy queries -> P119
R: publishing without expectation tests; silent schema drift past the gate; freshness SLOs nobody measures; notebooks shipped as contracts

## Worked chains

Common task shapes pre-resolved through the union rule; calibration
for the traversal.

| Task statement | Nodes | Emitted set (beyond shared mandatory) |
|---|---|---|
| "Split a restaurant bill among friends, store shares, charge retry-safe" | N03 + N02 | T1, T33, P42, P47, T27, P11, P12; plus P24 + P51 on the payment call (N07) |
| "Agent reads support emails and issues refunds" | N05 + N04 + N03 | T48, T50, P33, P37, P31 (emails are untrusted), T31, T32, T19, P36 (refund needs approval diff), T27 + P11 ledger entries |
| "Paginated admin table over a multi-tenant audit log" | N01 + N10 | P7, T8, P41; plus P43 if PII is stored, P4 on render |
| "Rewrite the billing ingest path" | N13 + N21 | P6, P19 (ledger checksums), P58, P59 at the legacy seam, P44 expiries on routing flags |

## Maintenance rules

1. New node: a task class appearing in three or more estate repos, with
   M drawn only from canon IDs and R edges citing a refusal (R1-R12) or
   a named failure mode. K lines carry the classification keywords.
2. Node edits are canon changes: CHANGELOG entry; M additions that
   promote a non-baseline pattern need an ADR.
3. The graph never contradicts PATTERN-CORE §3; M sets are supersets of
   the baseline tier for their domain.
4. `scripts/route.py` parses the K/M/A/R format; run it as the format
   regression test after any edit (`make check` covers it via
   check-canon's structural pass plus a route smoke call).

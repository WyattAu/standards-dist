# Field VI: Runtime Operations (P51–P54, P62–P63)

Battle-tested operational constructs for the failure modes that show
up in production on week one. All Proven; the risk here is skipping
them, not the pattern being wrong.

### P51 · Circuit breaker
**Failure.** A down dependency turns every caller into a retry machine; wasted work and connection storms widen the outage.
**Mechanism.** Per-dependency state machine: closed (normal) trips open on the failure-rate threshold, open fails fast with no network, half-open probes with bounded concurrency. Trip and reset decisions consume the same signals as P24 budgets.
**Analysis.** Proven (Nygard, "Release It!"; resilience4j; the estate's `breaker` kit). Baseline-tier next to P24 for all outbound clients. Refuse nowhere for network calls; the only design choice is the fallback value when open.
**Links.** P24 (retry budget feeds the trip decision), T35 (the server-side twin), P52 (bulkheads partition what the breaker guards).

### P52 · Bulkhead isolation
**Failure.** One exhausted shared resource (a DB pool eaten by slow report queries) starves unrelated work that shares it.
**Mechanism.** Partition every shared resource pool (connections, threads, memory budgets) by dependency or criticality tier; exhaustion in one partition cannot propagate to another.
**Analysis.** Proven (ship-bulkhead doctrine, "Release It!"). Adopt wherever two failure domains share a pool. Refuse for genuinely single-purpose services where one pool is one domain.
**Links.** P27 (criticality tiers are the partitioning key), T42 (the node-level version), P51.

### P53 · Dead-letter quarantine
**Failure.** One malformed or poisoned message blocks a consumer forever; the whole stream stalls behind it.
**Mechanism.** Bounded retries, then quarantine the message to a dead-letter stream with its error class and original metadata; DLQ depth is alerted; replay tooling re-injects after the fix.
**Analysis.** Proven (Kafka/SQS standard practice). Refuse nowhere for queue consumers; the design choices are retry count and DLQ schema, both small.
**Links.** T32 (the producing side), P18 (schema drift is the usual poison), P42 (quarantine is a wide event).

### P54 · Inbound webhook receiver hardening
**Failure.** Webhook receivers trust sender claims: forged deliveries mutate state, duplicates double-apply, replays resurrect old events.
**Mechanism.** Verify the HMAC signature before parsing; return 2xx after persisting the raw payload, process asynchronously with T33 dedupe on the delivery ID; tolerate reorder by re-pulling current state (P9 semantics) rather than trusting event order.
**Analysis.** Proven (Stripe/GitHub receiver doctrine). Refuse nowhere for inbound webhooks; inline processing in the HTTP handler is always wrong at scale.
**Links.** P9 (the outbound thin-ping twin), T33, T50 (if the payload feeds an agent, it is untrusted input: P31).

### P62 · Graceful drain
**Failure.** Deploys and scale-in drop in-flight requests and orphan background tasks mid-step.
**Mechanism.** Flip readiness first (stop receiving), finish or checkpoint in-flight work under a deadline, hand off queue ownership, cancel children in dependency order through the T11 nursery, exit zero within the orchestrator's grace period.
**Analysis.** Proven (Kubernetes lifecycle practice). Baseline for long-lived estate processes. Refuse nowhere that runs under an orchestrator; a process that cannot drain corrupts its own restart.
**Links.** T11 (ordered cancellation), T19 (checkpoint instead of finish), P23 (scope teardown).

### P63 · Trace-context propagation
**Failure.** One user action touches five services; no artifact ties the five log streams together, so incident triage is archaeology.
**Mechanism.** Propagate W3C `traceparent`/`tracestate` on every hop (HTTP, queue messages, spawned tasks); inject the context into wide events (P42) and into spawned work; sample at the edge once, propagate the decision everywhere.
**Analysis.** Proven (W3C Trace Context; OpenTelemetry default). Baseline via N11 telemetry setup. Refuse nowhere in service estates; single-process scripts skip it.
**Links.** P42 (context lands in the wide event), P30 (recorder tags the scope), T38 (causal tokens are the data-plane analog).

### P101 · Scheduled chaos experiments
**Failure.** Fault tolerance proven in CI is untested in production topology; the first real failure runs failure paths that have never executed with real traffic, real timeout values, and real dependency graphs.
**Mechanism.** Schedule experiments in production with a written hypothesis ("losing the cache for ten minutes keeps p99 under budget"), minimal blast radius (one instance, one tenant cohort), an abort condition wired to P45 signals, and a required post-experiment write-up; every finding converts into a new CI fault case (P29) so the same failure cannot surprise twice.
**Analysis.** Proven (Netflix ChAP and the Simian Army lineage; the Principles of Chaos). Refuse chaos without hypothesis, abort condition, or blast-radius cap; that is an outage with a calendar invite.
**Links.** P29 (CI fault injection is the rehearsal; production is the exam), P45 (abort signals), P51, P52, P53 (the mechanisms under test), P83 (experiment events are audited).

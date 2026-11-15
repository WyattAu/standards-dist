# Field V — Security, Observability & Software Evolution (P41–P50)

Constructs where the alternative is trust in human vigilance, and the
vigilance always eventually fails.

### P41 · Type-injected tenant RLS scopes
**Failure.** IDOR happens the day one developer forgets `WHERE tenant_id = ?` in a new query.
**Mechanism.** Repository handles instantiate only from a signed `TenantCapability` that binds Postgres RLS session variables (or injects the AST predicate); cross-tenant queries are unrepresentable, not forbidden.
**Analysis.** Proven (Postgres RLS itself; capability injection is common practice in multi-tenant SaaS). Baseline-tier for every estate multi-tenant service (accessctl is the reference). Refuse for single-tenant deployments.
**Links.** T8 (capability shape); T46 (Datalog policy decides what the capability may ask).

### P42 · Wide-event tail-sampled accumulators
**Failure.** Scatter-shot `logger.info()` floods log bills with uncorrelatable noise and hides request-level context.
**Mechanism.** One mutable `RequestWideEvent` map rides the trace context; emit one canonical JSON line at request end; retain 100% of errors/slow-p99 and ~1% of healthy fast traces.
**Analysis.** Proven (Honeycomb wide-events doctrine). Baseline-tier for estate services. Refuse nowhere server-side; tail-sampling needs a collector that supports it (OTel).
**Links.** P30 (ring buffers capture the pre-crash window the wide event cannot); P45 (burn-rate alerts consume the same telemetry).

### P43 · Crypto-shredding per-entity DEKs
**Failure.** Immutable event logs and backups violate GDPR deletion; PII sits inline forever.
**Mechanism.** Encrypt each entity's PII with a dedicated DEK in an isolated key table; deletion drops one key row in O(1), rendering all historical logs and backups unreadable.
**Analysis.** Proven (standard in event-sourced stacks under GDPR). Adopt in auditlog and any estate store with PII in append-only history. Cost: key management hygiene (rotation, KMS backing). Refuse where PII is truly absent — do not crypto-shred nothing.
**Links.** T21 (event sourcing's deletion answer); P4 (redaction is the live-path complement to shredding the history).

### P44 · TTL-enforced feature flag pruning
**Failure.** Flags accumulate until nobody knows which `if (flags.newCheckoutV2)` branches are safe to delete.
**Mechanism.** Every flag declaration carries `expiresAt` and owner; CI fails past expiration; an automated codemod strips the stale branch and its dead code.
**Analysis.** Proven doctrine (flag hygiene at every mature shop; the enforcement CI is the construct). Adopt estate-wide: flags without an expiry date do not merge. Refuse for permanent configuration — that is P47's job, not a flag's.
**Links.** P47 (epoch-pinned config for the flags that survive); P48 (the same CI-gate shape).

### P45 · Multi-window SLO burn-rate gates
**Failure.** Static thresholds (`CPU > 80%`) page on brief self-healing spikes; alert fatigue trains engineers to ignore pages.
**Mechanism.** Paging fires only on dual-window error-budget burn velocity: e.g. 2% of the 30-day budget burned in 1h **and** confirmed over 5m (Google SRE workbook multi-window, multi-burn).
**Analysis.** Proven (SRE workbook ch. 5; adopted industry-wide). Baseline-tier for estate monitoring (argus). Refuse for single-instance dev boxes.
**Links.** P42 (wide events are the signal); T35 (adaptive limits act where burn-rate alerts page).

### P46 · Static dependency capability manifests
**Failure.** One compromised transitive dependency inherits full access: `process.env`, filesystem, outbound sockets.
**Mechanism.** Third-party modules run behind explicit manifests (`{ fs: false, net: ["api.stripe.com"], env: [] }`) enforced by WASM/SES realms or runtime syscall filters.
**Analysis.** Emerging in JS (SES hardening), Proven in concept (WASI, landlock/seccomp). Adopt pragmatically: syscall filters around the riskiest parsers; full SES for anything executing untrusted plugin code. Refuse for dependencies that legitimately need broad I/O — attenuate the interface instead.
**Links.** T8 (OCap substrate); P29 (fault-injection and sandboxing share the I/O seam).

### P47 · Epoch-pinned config snapshots
**Failure.** Live-reloaded config tears requests: step 1 sees `threshold_v1`, step 4 sees `threshold_v2`.
**Mechanism.** Request ingress binds an immutable `ConfigSnapshot` pointer into the request context; the whole request, including spawned tasks, reads one epoch.
**Analysis.** Proven (MVCC by construction; standard in config systems that learned the hard way). Baseline-tier estate-wide — cost is one pointer copy. Refuse nowhere.
**Links.** T29 (the snapshot substrate); P28 (forked workers must pin their snapshot epoch); T26 (the data-layer analog).

### P48 · Compile-time acyclic layering fitness gates
**Failure.** Architecture boundaries erode via shortcut imports until the dependency graph is a ball of mud.
**Mechanism.** Layer constraints (`Domain → ∅`, `UseCase → Domain`, `Infra → UseCase|Domain`) as build-time AST dependency assertions that fail PRs on cycles or inversions.
**Analysis.** Proven tools (dependency-cruiser and kin in JS; clippy module groups in Rust). Adopt in estate app repos with real layering ambitions; refuse for small kits where the module tree *is* the layering.
**Links.** T46 (the same fixed-point analysis over import facts); P49 (impact fingerprints ride the same graph).

### P49 · Call-graph impact test fingerprinting
**Failure.** CI suites grow linearly with repo size until 45-minute builds stall velocity.
**Mechanism.** Merkle hashes over each test's transitive call graph and fixture inputs; commits outside a test's dependency cone skip it in O(1).
**Analysis.** Emerging-to-proven (Bazel/Turborepo target graphs are the coarse version; call-graph precision is newer). Adopt in monorepos after target-level selection stops paying; refuse where the suite runs under ~5 minutes — the machinery costs more than it saves.
**Links.** T17 (incremental query graphs are the compile-time twin); T28 (content addressing).

### P50 · Hermetic synthetic-twin envelopes
**Failure.** Code passes against empty local mocks, then fails in production on skewed data, missing indexes, or OS library mismatches.
**Mechanism.** One content-addressed dev/CI envelope: pinned system libraries, compilers, and anonymized production-distribution synthetic DB snapshots — local runs match production geometry.
**Analysis.** Proven direction (the estate's Nix shells are half of this; the synthetic-data half is emerging). Adopt incrementally: pin libraries first (done via Nix), then distributions for the DBs where plans go wrong (Postgres statistics). Refuse where data distribution is not load-bearing.
**Links.** Nix devShell invariant (OMNI-CORE 11b); P18 (synthetic data must pass the same drift canaries); T36 (the simulation layer above the data layer).

# Field X: Deployment & Release (P75–P79)

Constructs for shipping risky changes without betting the service on
one event. All Proven; the failure mode they share is binary rollout
(all-at-once, no evidence, no revert path).

### P75 · Canary release with automated analysis
**Failure.** A bad release rolls to 100% before anyone looks at a dashboard; the rollback decision is made by a human after the page.
**Mechanism.** Shift traffic in steps (1%, 10%, 50%); an analyzer compares SLIs (error rate, latency, saturation) between canary and baseline at each step; regression aborts and reverts automatically; promotion requires the analysis gate, not a feeling.
**Analysis.** Proven (Argo Rollouts, Flagger, Kayenta lineage). Adopt for estate services with real traffic; refuse for dev-only deployments where a canary costs more than the outage.
**Links.** P45 (the SLIs are burn-rate signals), P78 (cohort exposure generalizes the traffic split), P79 (canary promotes the same digest, never a rebuild).

### P76 · Blue-green with instant revert
**Failure.** Reverting a bad release takes as long as deploying, so the bad version serves while the fix rebuilds.
**Mechanism.** Two full environments (blue = live, green = next); deploy and warm green, flip the router atomically; revert is a flip back, seconds not minutes; database migrations are expand-contract (N13) so both colors run against both schema shapes.
**Analysis.** Proven (standard platform practice). Adopt where revert speed dominates and cost of doubled capacity is acceptable; refuse where state lives only in the process (use P75 instead).
**Links.** N13 (expand-contract is what makes two versions coexist), P62 (drain the old color, do not kill it).

### P77 · Shadow traffic (dark launch)
**Failure.** A rewrite's first real production traffic is its first real production input; synthetic tests never contained the input distribution (P50's failure mode at the traffic layer).
**Mechanism.** Mirror live requests to the new implementation; responses (and side effects, carefully gated) are compared against the serving path's; divergence metrics drive the go/no-go; users never see shadow output.
**Analysis.** Proven (unicorn-era dark launch doctrine; standard at scale). Adopt for high-risk rewrites of read paths with P6-style diff comparison. Refuse for write paths where double side effects are unsafe (use N21's strangler slicing instead).
**Links.** P6 (parity comparison is the analyzer), P50 (synthetic envelopes seed the shadow before real traffic does), P28 (forked sandboxes serve shadow copies).

### P78 · Progressive exposure cohorts
**Failure.** A feature flag flips to everyone at once; the 1% who would have hit the bug are not a sample, they are casualties.
**Mechanism.** Exposure is an axis: internal staff, then 1%, 5%, 25%, 100%, with a metrics gate between cohorts; cohorts are stable (a user does not oscillate between experiences); the ramp is recorded and auditable.
**Analysis.** Proven (staged rollout practice at every large platform). Adopt for user-visible changes shipped via P44 flags. Refuse for server-internal changes where P75 traffic-shifting is the honest axis.
**Links.** P44 (flags gate the cohort), P75 (cohort gate is a canary analysis over cohorts), P5 (client caches respect the cohort epoch).

### P79 · Content-addressed release artifacts
**Failure.** "What is running in prod?" is answered by rebuilding: the artifact in prod is not bit-identical to the one CI tested, and provenance is folklore.
**Mechanism.** Build once, promote by digest (T28): every environment runs the exact artifact CI verified; SBOM and provenance attestation (sigstore/cosign) attach at build; admission control rejects undigested or unattested images; rollback = redeploy the previous digest.
**Analysis.** Proven (sigstore, supply-chain security practice; OMNI-CORE 11h/11j make it estate law). Baseline for estate deployments. Refuse nowhere; rebuilding for an environment is the anti-pattern.
**Links.** T28 (content addressing), OMNI-CORE 11h/11j (SBOM + attestations), P76 (both colors are digests), P44 (flags live in config, not in rebuilt artifacts).

### P98 · Dress-rehearsal release gate
**Failure.** The first time a release executes its full production sequence, with real data volumes, real operation order, and real integrations, is in production; the gaps between staging and production surface as incidents.
**Mechanism.** A release gate that runs the complete production sequence against a production-fidelity environment: same entry points, same data geometry (P50), same runbook, same timing; the rehearsal must pass the same health gates the release will use; a rehearsal failure is a release blocker, and the drain is rehearsed too.
**Analysis.** Proven (the "test like you fly" doctrine; SpaceX static-fire practice; Jane Street shadow-trading strategies before capital). Refuse rehearsals on toy data and rehearsal gates looser than release gates; both are theater.
**Links.** P77 (shadow traffic is continuous rehearsal), T36 (the simulation layer beneath it), P50 (production geometry), P62 (the drain is part of the sequence).

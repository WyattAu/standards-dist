# Field XIII: Safety & Margin Discipline (P93–P95, P100)

Constructs from avionics, defense, and launch practice: keep serving
when components die, detect the walking dead, vote on decisions, and
never spend the last percent of a budget. Shared failure mode: a
single undetected failure, or a resource consumed to exactly 100%.

### P93 · Fail-operational degraded modes
**Failure.** Systems designed fail-safe stop entirely when a component degrades; availability of the *function* dies with availability of one *component*, so losing recommendations takes down checkout.
**Mechanism.** Define service tiers at design time: full, degraded (core function only, non-essential features shed), minimal (read-only, queue-and-forward). Each tier has entry and exit criteria wired to health signals (P45); degradation is automatic, user-announced, and recovery is automatic when the component returns. Capacity is budgeted per tier.
**Analysis.** Proven (the avionics fail-operational vs fail-safe distinction; load-shedding practice at scale). Adopt for any user-facing service with separable features. Refuse degradation paths without tested *exit* criteria; a "degraded" tier that is actually a broken tier is worse than an outage because it is silent.
**Links.** P27 (criticality is the shedding key), P51 (breaker open is a degraded-mode trigger), T35 (load-adaptive tier switching).

### P94 · Watchdog + heartbeat supervision
**Failure.** A process wedges (deadlock, GC spiral, stuck event loop) without dying; nothing restarts it because nothing can see it is stuck; users discover the failure.
**Mechanism.** The supervised component publishes a heartbeat whose meaning is *progress* (an advancing sequence number), not liveness; an independent supervisor (hardware timer, systemd watchdog, or separate process) restarts on missed deadline; restarts count, and flapping trips the component into a maintenance state.
**Analysis.** Proven (hardware watchdog timers, systemd `WatchdogSec`, Kubernetes liveness probes). Refuse heartbeats that mean "not crashed"; a stuck loop sends heartbeats happily.
**Links.** T12 (supervision trees above the watchdog), P62 (drain before the forced restart), P30 (ring buffer flushes the wedge history on trip), P51 (flapping is a circuit to open).

### P95 · 2oo3 voting (redundant-channel consensus)
**Failure.** A single sensor or single computation path has undetectable failure modes; acting on one silently-wrong input is worse than acting on no input.
**Mechanism.** N redundant channels produce the decision input; a 2-out-of-3 (k-of-n) voter combines them; disagreement beyond threshold selects the safe default and raises the discrepancy as an audited event (P83). Channels must be independently sourced or clocked, or common-mode failure defeats the redundancy entirely.
**Analysis.** Proven (2oo3 flight computers; the spacecraft reliability literature). Refuse redundant *copies* of the same binary on the same host; that is one channel wearing three name tags. Refuse voting on high-frequency data without a latency budget for the vote itself.
**Links.** P83 (discrepancies are audited facts), P18 (per-channel drift canaries catch slow divergence), P14 (voting is for decisions; deterministic reduction is for numeric reproducibility).

### P100 · Margin budgets as first-class numbers
**Failure.** Bounded resources (CPU headroom, disk, latency budget, memory) are consumed invisibly; the system works until the day it sits at 100% and can absorb neither a spike nor an emergency.
**Mechanism.** Every bounded resource carries a margin account: a stated total with units (PRESENT PR-5), a reservation ledger where each feature or tenant registers its claim, and a burn-down review on every addition. Margin below the reserve floor blocks new claims; a budget that cannot say no is decoration.
**Analysis.** Proven (NASA and defense margin management; capacity-planning doctrine). Refuse advisory-only ledgers; unenforced margins are vibes with units.
**Links.** X4 (resource envelopes are the compile-time cousin), P17 (margin expressed as tokens), P22 (fair shares are claims on the account), P27 (emergencies draw down the reserve deliberately).

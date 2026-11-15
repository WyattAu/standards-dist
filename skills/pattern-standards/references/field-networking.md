# Field XV: Networking & Time Discipline (P103–P105)

Constructs for the layer every outage report actually names: calls that
hang, resolvers that lie, and jobs that run twice or never. Shared
failure mode: time and identity treated as reliable when they are
best-effort.

### P103 · Deadline propagation
**Failure.** Every hop sets its own generous timeout; sequential hops compose into 30-second user waits; retries fire on requests whose caller already gave up, amplifying load exactly when the dependency is already struggling.
**Mechanism.** The entry point stamps a deadline (absolute time or remaining budget) into the request context; every outbound call carries `min(own timeout, remaining budget)`; workers check the budget before starting expensive work; expiry returns a typed budget-exceeded error (P72), never a hang. Fire-and-forget work issues its own fresh budget instead of inheriting a dead caller's.
**Analysis.** Proven (gRPC deadline propagation; the default stance in every serious RPC framework). Mandatory in N07 and N30. Refuse nowhere on a call chain; the only design choice is what the budget-exceeded error drops first (P27 answers that).
**Links.** P24 (retry budgets stop the amplification deadlines start), P51 (breakers trip faster under propagated deadlines), P42 (budget-exceeded is a wide-event field), P40 (the same budget idea over dollars).

### P104 · DNS discipline
**Failure.** DNS is treated as reliable plumbing; a resolver blip becomes a full outage, a failed lookup is cached as permanent, and a stale record serves traffic to a dead address.
**Mechanism.** Resolution carries conservative timeouts; positive and negative answers are cached with short TTLs; a last-known-good address set is retained stale-while-error; failures re-resolve rather than poison the cache; end-to-end health checks verify the resolved chain, not the resolver.
**Analysis.** Proven (SRE doctrine; the incident literature is unanimous that DNS outages are availability outages). Refuse hard-coded IPs as the fallback plan for anything dynamic; resolving inside tight loops is its own refusal.
**Links.** P29 (Faulty<IO> injects resolution failures in CI), T36 (deterministic replay of the resolver's worst day), T41 (hash rings presuppose a working resolution layer).

### P105 · Overlap-guard scheduled jobs
**Failure.** Distributed cron runs the job twice (two hosts, or a previous run overrunning its window) or zero times (the leader died mid-window); missed-window semantics are undefined and usually undocumented.
**Mechanism.** Every schedule carries: a coordination gate (advisory lock or lease, T34-shaped), an explicit overlap policy (skip, queue, or kill-and-replace), a missed-window policy (run-once-late or skip-with-alert), and observability so a job that never ran pages (P45) instead of hiding.
**Analysis.** Proven (Quartz misfire policies, Kubernetes CronJob `concurrencyPolicy` and `startingDeadlineSeconds`; every scheduler reinvents these knobs). Refuse uncoordinated crontabs on multiple hosts; refuse jobs whose success is unobservable.
**Links.** P56 (backfills are the catch-up form), T19 (long jobs belong in durable workflows, not cron), T34 (the gate is a fencing token), P83 (runs are audited facts).

# Field II — Quant, Numerical & Financial Integrity (P11–P20)

Constructs for the estate's quant/accounting paths, where silent
numerical corruption outranks every other failure class.

### P11 · Remainder-preserving partition operators
**Failure.** `amount * weight` splits lose or create pennies: `sum(shares) ≠ total` after naive division and rounding.
**Mechanism.** One algebraic primitive `partition(Total, Weights) -> Shares` using largest-remainder (Hamilton) allocation with the residual assigned by deterministic rank; conservation `Σ Sharesᵢ = Total` holds at the atomic sub-unit, every call.
**Analysis.** Proven (apportionment mathematics older than software; standard in billing systems). Baseline-tier for billing-kit fee/inventory splits. Refuse nowhere money divides; integer minor-units only, never floats.
**Links.** T27 (the ledger entries the shares produce); P12 (units prevent feeding the wrong scale into the weights).

### P12 · Phantom dimensional algebra (`Qty<Unit, Scale>`)
**Failure.** Basis points vs decimals, USD vs EUR, log vs linear returns mix silently; results look plausible and are wrong.
**Mechanism.** Units as compile-time exponent vectors; `USD + EUR` fails to compile, `Price<USD/Share> * Qty<Share>` synthesizes `Amount<USD>` automatically.
**Analysis.** Proven (uom/nalgebra lineage in Rust, F# units of measure). Adopt in accounting-spec and any quant kernel. Cost: generic surface area — keep the unit vocabulary small (currency, share, bps, ratio). Refuse in UI/prototype code where units are singular and obvious.
**Links.** P11 (partition is unit-preserving); P15 (Finite<T> composes with unit scalars).

### P13 · Causal horizon guards (`AsOf<T, t_avail>`)
**Failure.** Backtests and feature pipelines leak future knowledge via restatements and EOD joins; results flatter reality.
**Mechanism.** Stamp every datum with knowledge-availability time `t_avail`; the simulation context carries a cursor and rejects/masks any datum with `t_avail > t_sim_now`. Joins default to as-of semantics, not equality-on-date.
**Analysis.** Proven discipline in institutional quant; library support is thin, so this is a repo-level invariant. Adopt in all estate backtesting paths. Refuse nowhere in that class — lookahead bias is not detectable downstream.
**Links.** T26 (bitemporal storage supplies the stamps); P8 (tzdata as-of: the same instinct for time rules).

### P14 · Fixed-topology parallel reductions
**Failure.** Multi-threaded `sum()` drifts run-to-run because `(a+b)+c ≠ a+(b+c)` and arrival order varies.
**Mechanism.** Reduction over a deterministic binary tree keyed by logical index (or Kulisch superaccumulator for exact fixed-point), never over arrival order; 1 core and 64 cores produce bit-identical output.
**Analysis.** Proven (HPC/ML reproducibility practice). Adopt in quant kernels where diffs must be meaningful; refuse where floating-point tolerance is already the contract.
**Links.** T20 (mechanical sympathy family); P20 (deterministic replay depends on it).

### P15 · Provenance-trapped NaN (`Finite<T>`)
**Failure.** One NaN/Inf poisons a matrix chain; the origin (division by zero? cancellation?) is lost by the time it surfaces.
**Mechanism.** Checked scalar type traps non-finite creation at the originating operator with operand snapshots; optional condition-number κ warnings where precision loss is predictable.
**Analysis.** Proven concept (debug-mode NaN canaries), thin library support — a kit-level type. Cost: operator plumbing; scope to kernel boundaries, not the whole app. Refuse in UI math where a NaN is visibly wrong anyway.
**Links.** P12 (units + finiteness compose); P18 (distribution canaries catch the upstream data version of the same disease).

### P16 · Half-life validated quotes (`Quote<T, Window, Decay>`)
**Failure.** Engines trade on stale cached quotes during feed stalls; staleness is invisible at the call site.
**Mechanism.** `.mid()` requires passing `now`; expired quotes fail type-checked access or widen the bid-ask by the attached decay function, making staleness a priced input rather than a silent error.
**Analysis.** Proven concept in market-data infrastructure; Emerging as a reusable library shape. Adopt in any estate pricing path. Refuse for research notebooks where staleness analysis is the point.
**Links.** P21 (the general staleness-contract pattern this specializes); P20 (the replay envelope stamps quote ages).

### P17 · Tokenized risk-budget capabilities
**Failure.** Strategies each pass local checks while together blowing aggregate VaR/leverage limits.
**Mechanism.** A central allocator issues finite, revocable tokens (delta, notional, margin); the order gateway locks unforgeable worst-case tokens before submission; over-budget orders fail at the gate.
**Analysis.** Proven concept (exchange risk engines; quota systems by analogy); implementation is bespoke. Adopt when ≥2 estate strategies share one account/broker. Refuse for single-strategy sandboxes.
**Links.** T8 (OCap: the token *is* the authority); P40 (the same attenuation pattern over spend).

### P18 · Online distribution canaries
**Failure.** Upstream feeds silently shift scale (split-adjusted vs raw, null spikes) without a schema error; downstream models degrade quietly.
**Mechanism.** Streaming quantile/moment trackers at deserialization boundaries; quarantine the stream when batch Wasserstein/KS distance breaches baseline bounds.
**Analysis.** Emerging (drift monitors exist in ML platforms; embedding them at the *deserialize* boundary is the sharp idea). Adopt for estate market-data ingestion. Cost: baseline maintenance per feed. Refuse for human-in-loop data entry.
**Links.** P20 (the envelope that carries quarantine flags); P42 (wide events record the quarantine decision).

### P19 · Homomorphic Merkle ledger checksums
**Failure.** Reconciling millions of rows between two ledgers to find one wrong cent takes full-table scans.
**Mechanism.** Incremental XOR/additive homomorphic hashes bucketed by time/account; two systems compare bucket digests and descend only into mismatched buckets — O(log N) round trips to the exact record.
**Analysis.** Emerging (set-reconciliation literature; Invertible Bloom Filters are the proven cousin). Adopt for estate ledger replicas and post-migration verification (pairs with P6). Refuse for small tables where a full scan is one query.
**Links.** T28 (Merkle DAGs); P6 (parity gates use this as the diff oracle).

### P20 · Unified replay clock envelopes
**Failure.** Live engines and backtesters diverge subtly: separate codebases, separate ordering assumptions, separate bugs.
**Mechanism.** One `EventEnvelope(seq, eventTime, watermark)` state machine for both live WS ticks and historical files; the shared clock never reads wall-clock `Date.now()` — sim-time is injected.
**Analysis.** Proven direction (event-sourced trading systems). Adopt for all estate trading/ingest engines. Cost: forcing historical data into envelope shape — pay once at adapters.
**Links.** P14 (deterministic reductions inside); T36 (DST drives the same envelope in CI).

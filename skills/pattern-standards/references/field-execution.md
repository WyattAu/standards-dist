# Field XII: Execution & Trading (P87–P92)

Constructs for the estate's live trading paths. Shared failure mode:
an action taken in one clip, without measurement, or without a halt.
All Proven; most are venue-mandated in spirit.

### P87 · Order slicing (TWAP/VWAP)
**Failure.** A parent order hits one venue in one clip; impact moves the price against the trader before the order completes.
**Mechanism.** Decompose the parent into child orders over a profile: uniform time slices (TWAP) or a historical volume curve (VWAP); replan remaining children on every fill; each child passes the P17 risk gate independently.
**Analysis.** Proven (execution-algo standard). Refuse for thin illiquid names where a visible slice footprint leaks intent; adapt the profile or refrain.
**Links.** P17 (per-child risk tokens), P20 (children live in the replay envelope), P88 (child routing).

### P88 · Smart order routing
**Failure.** Orders rest on one venue while a better effective price sits elsewhere, because fees, rebates, and fill probability were never in the routing decision.
**Mechanism.** Route each child by effective cost: price plus fee minus rebate plus latency risk, weighted by fill probability from live quotes (P16); continuously re-route the unfilled remainder; maintain a venue blackout list as config (P47 epochs).
**Analysis.** Proven (SOR is core broker infrastructure). Refuse for single-venue accounts; the model is the value, keep it simple before multi-venue exists.
**Links.** P16 (quotes feed the cost model), P87 (children are the routing units), P18 (canaries on venue feed drift).

### P89 · Fill reconciliation + break detection
**Failure.** Fills arrive late, duplicated, or out of order; internal positions drift from broker truth; breaks surface at month-end when they cost the most.
**Mechanism.** Expected-fills ledger versus broker confirmations, matched on execution IDs (P60-shaped, T33-stable); mismatches open break tickets into an ops queue (P53 shape: bounded retry, quarantine, replay after fix); positions adjust only from reconciled facts, never from raw feeds.
**Analysis.** Proven (post-trade standard). Refuse nowhere with a broker on the other side.
**Links.** T27 (positions are derived from reconciled entries), P53 (the break queue), P20 (fills enter through the envelope).

### P90 · Slippage benchmarking (TCA)
**Failure.** Nobody can say what execution cost versus the decision price; strategy P&L conflates alpha with execution cost, so bad routing hides inside good signals.
**Mechanism.** Benchmark every fill against arrival price and interval VWAP; record slippage per order, venue, and algo into the rollup store (P61); track regressions per strategy with the same rigor as PnL.
**Analysis.** Proven (transaction-cost analysis standard). Refuse for strategies where the decision price is undefined (no clean signal time); measure what you can define.
**Links.** P61 (the rollups), P13 (arrival is an as-of decision), P14 (deterministic aggregation for comparable numbers).

### P91 · Market-data budget adaptation
**Failure.** Venue message-rate limits are violated during bursts; the feed disconnects exactly when volatility (and value) spikes.
**Mechanism.** Throttle subscriptions to each venue's budget with a priority order: top-of-book survives first, depth and trades drop first; a T35-style loop adapts pacing to the observed budget; reconnect with hardened sessions (P54 semantics) and resume tokens.
**Analysis.** Proven (venue feed-handler practice). Refuse nowhere that consumes venue feeds; the budget is a hard constraint, not a suggestion.
**Links.** T35 (the adaptation loop), P16 (quotes the budget protects), P18 (canaries verify the adapted stream stays honest).

### P92 · Kill switch
**Failure.** A rogue strategy or fat-finger order keeps trading while humans look for someone with deploy rights; every additional second is P17 budget burning.
**Mechanism.** One authenticated halt capability wired into every order path: the gateway checks halt state before the risk gate; the state store failing closed (unavailable means halted); drills run monthly; clearing requires two-party approval and lands in the audit chain (P83).
**Analysis.** Proven (exchange/venue-mandated doctrine; flash-crash literature). Refuse nowhere for live trading; a path without a halt check is not an order path.
**Links.** P17 (the gate next to the halt check), T8 (halt authority is a capability), P83 (halt and clear events are audited), P62 (drain after halt, in order).

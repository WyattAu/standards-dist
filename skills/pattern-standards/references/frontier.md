# Frontier; Next-Generation Constructs (X1–X7)

Research-grade constructs that break the assumptions classic patterns
presuppose: exact epistemic values, per-runtime programs, imperative
branching, hand-authored implementations, arbitrary CRUD mutation,
run-to-completion semantics, and text as the code substrate. Adoption
is pilot-tier by definition: expect tooling gaps, budget for them, and
write an ADR before anything here becomes load-bearing.

### X1 · Epistemic types & decision-theoretic collapse (`Uncertain<T>`)
**Failure.** Every boundary coerces uncertainty into crisp booleans (`score > 0.8`); the distribution is erased and downstream code decides on false precision. Magic thresholds scatter across services.
**Mechanism.** Values carry distributions/intervals through pure transformations (Monte Carlo, interval arithmetic, Bayesian updates). Business logic never thresholds; every irreversible side effect declares an asymmetric loss matrix: `collapse(belief, costFP, costFN)` decides at the boundary where the cost is stated.
**Analysis.** Emerging (interval arithmetic and probabilistic programming are proven tools; the everyday application pattern is not yet productized). Pilot in one decision path with real asymmetry (fraud block, auto-trade) before generalizing. Refuse where the threshold genuinely encodes a regulation.
**Status.** Pilot-tier. **Links.** P13 (as-of discipline is epistemic about *time*, this about *value*); P16 (decay widens uncertainty instead of hiding it).

### X2 · Choreographic tier-splitting
**Failure.** One logical interaction is hand-split across React/BFF/API/DB with DTOs, hooks, and schemas that drift.
**Mechanism.** Write one program with location-indexed types (`userId@Client`, `secretKey@Server`); a compiler projects endpoint programs plus wire schemas from the single source (Choral, HasChor lineage). Schema drift, ordering deadlocks, and client-side secret leaks become unrepresentable.
**Analysis.** Emerging research (choreographic programming is proven as PL theory, not yet as application tooling). Pilot shape: a typed-RPC layer with end-to-end inference (tRPC-like) delivers 70% of the value today at 10% of the risk; start there, adopt true choreography when tooling matures.
**Status.** Watch-tier (proxy pattern now, full pattern later). **Links.** T7 (session types are the per-endpoint core); T45 (hypermedia is the runtime-mediated version).

### X3 · Additive constraint manifolds
**Failure.** Business rules as imperative branch trees compose multiplicatively: rule #47 risks rules #1–46; order-dependence breeds bugs.
**Mechanism.** Rules register as additive terms over shared state: hard invariants (boundary conditions) and soft potentials (penalties/utilities); an incremental relaxation solver settles to a valid low-energy equilibrium and reports conflicts via dual variables (constraint provenance).
**Analysis.** Emerging (Cassowary proved it for layout; propagator networks are proven research; Sussman/Radul; domain application lacks ergonomic solvers). Pilot for a genuinely over-constrained domain (scheduling, pricing with many rules). Refuse where rules are few and orthogonal; a solver is overhead there.
**Status.** Pilot-tier. **Links.** T30 (e-graphs share the global-settle instinct for expressions); X1 (soft potentials carry uncertainty naturally).

### X4 · Specification-as-source (synthesized implementations)
**Failure.** Hand-written implementation bodies are canonical; tests and contracts are shadows. Swap-in of a faster/safer implementation risks invariant breakage every time.
**Mechanism.** The canonical module source is types + formal pre/post-conditions/invariants + resource envelopes; implementation bodies are disposable caches synthesized and verified against the spec (synthesis + property-based checking). Hot-path and debug variants interchange without invariant risk.
**Analysis.** Speculative-to-emerging (LLM synthesis + SMT/PBT verification is real today; the *inverted module structure* is not productized). Pilot only where invariants are crisp and testable (parsers, allocators, pure kernels). Do not bet estate repos on it yet.
**Status.** Watch-tier. **Links.** T49 (the generator-verifier loop it institutionalizes); T3/T4 (the interpreter seams it can specialize).

### X5 · Gauge-symmetric domain operators (Noether for state)
**Failure.** Generic CRUD setters (`setBalance`) plus validators let bugs create value, leak permissions, break parity; validation after mutation cannot catch what mutation spanned.
**Mechanism.** The module exposes only invariant-spanning group actions (split, merge, transfer, attenuate, delegate) whose algebraic closure lies inside the valid manifold. Illegal states have no generating operator; conservation by geometry, not by post-hoc validator.
**Analysis.** Emerging (double-entry ledgers are the proven special case; CRDT semilattices another; generalization is design discipline, not tooling; adoptable now by hand). Pilot in the next domain that conserves something: quotas, entitlements, inventory.
**Status.** Pilot-tier (discipline-only, no new tooling required). **Links.** T27 (the canonical instance); P17 (risk tokens as attenuations); T8 (OCap as capability conservation).

### X6 · Anytime optimal-stopping control flow (`Anytime<T, Quality>`)
**Failure.** Computation is binary: run to exact completion or hit a dumb timeout and throw. Timeouts waste budget below the utility knee and truncate above it.
**Mechanism.** Anytime operations emit monotonic refining approximations with live marginal-utility (∂U/∂t) and burn-rate (∂C/∂t); an outer scheduler allocates compute slices and halts each task when marginal value drops below marginal cost, committing the best valid state.
**Analysis.** Emerging (anytime algorithms and optimal stopping are mature theory; first-class language/library shape is not). Pilot inside agent loops and search/retrieval where quality is measurable mid-flight. Refuse where partial results are invalid; most transactional writes.
**Status.** Pilot-tier. **Links.** P32 (model cascades), T39 (hedging), P27 (shedding) are all special cases this unifies.

### X7 · Morphism-driven refactoring
**Failure.** Extensibility is pre-paid as speculative runtime abstraction (`IUserServiceFactory`, one implementation) because text-based refactoring across 50 files is feared.
**Mechanism.** Write maximally concrete code; extensibility lives in tooling: when the second implementation genuinely arrives, apply a behavior-preserving structural morphism (`extractAlgebraicBoundary(fn, traitSpec)`) over a content-addressed semantic graph (Unison-style hashing), updating every call site with an equivalence proof for existing behavior.
**Analysis.** Speculative as product (semantic-graph refactoring exists in fragments: GritQL, codemods, Unison; verified morphisms do not). Adopt the *doctrine* now; refusal R1 bans speculative factories; pay for abstraction only when the second implementation exists, then extract mechanically with heavy tests.
**Status.** Doctrine-tier (doctrine now, tooling later). **Links.** P49 (call-graph fingerprints find the blast radius); T28 (content addressing); T49 (verification gates the morphism).

# Foundations V; Declarative, Security & Probabilistic Interfaces (T43–T50)

Inverting control across render trees, cryptographic proofs, and
stochastic engines.

### T43 · Declarative tree reconciliation (UI = f(state))
**Failure.** Manual DOM/listener synchronization spaghetti; UI and state drift by construction.
**Mechanism.** UI as a pure function of state; a reconciler (fiber/signal-graph) computes the minimal mutation batch.
**Analysis.** Proven (React, SolidJS; the estate frontend baseline). Refuse nowhere; remaining choices are granularity (VDOM vs. signals; T15) not paradigm.
**Links.** T15 (signal DAGs remove the diffing cost); P3 (query-plan hoisting feeds the render tree).

### T44 · Resumable closure serialization
**Failure.** Client boot re-executes the entire component tree to rebuild interactivity; hydration is O(tree) CPU on every load.
**Mechanism.** Serialize suspended execution boundaries and handler closures into the payload (Qwik's resumability); clients resume lazily in O(1) interactive units.
**Analysis.** Proven (Qwik; partytown-adjacent). Cost: framework lock-in and closure-serialization constraints. Refuse on content sites where estate default is Astro/no-hydration; this pattern is for genuinely interactive islands.
**Links.** T43 (same render contract, different execution model); P3 reduces the data half of the same boot cost.

### T45 · HATEOAS / hypermedia state transitions
**Failure.** Clients hard-code server state machines; every workflow change breaks deployed clients.
**Mechanism.** Server payloads embed the valid next transitions (links/forms); clients stay generic interpreters of a server-owned state machine.
**Analysis.** Proven (REST maturity's level 3; HTMX revival). Cost: media-type design discipline. Adopt for server-driven UI and admin tools; refuse for tight SPA/API pairs where an OpenAPI contract (T6+codegen) already pins the machine.
**Links.** P10 (wizard state machines server-side); X2 (choreography is the full compile-time version of the same goal).

### T46 · Fixed-point Datalog rules over fact stores
**Failure.** Authorization and dependency logic sprawl through imperative checks nobody can audit as a whole.
**Mechanism.** Declare recursive relational rules evaluated to fixed point over immutable facts (Oso, Cedar's foundations, Datomic queries); the rule set is inspectable data.
**Analysis.** Proven (Datalog since 1970s; production authorization engines now). Adopt for accessctl-style policy: roles, delegations, denial chains. Refuse for simple boolean checks; a predicate is not a rule engine.
**Links.** P41 (RLS scoping is the enforcement half; Datalog is the policy brain); P48 (layering gates are the same analysis over import facts).

### T47 · Prove-then-verify (succinct zero-knowledge offload)
**Failure.** Expensive or untrusted computation must be trusted on faith, or re-executed to check.
**Mechanism.** Produce a succinct proof of the state transition; verifiers check in O(1)/polylog without re-execution (STARK/SNARK).
**Analysis.** Emerging-to-proven for specific shapes (rollups, zkVMs like RISC Zero); impractical for general CRUD; proof generation cost dominates. Adopt when an external party must trust our computation without re-running it.
**Links.** T28 (Merkle commitments are the data side); P34 (metamorphic gates when no hard verifier exists); T49 (the statistical sibling).

### T48 · FSM / grammar-constrained decoding
**Failure.** LLMs emit malformed JSON, wrong enum values, or broken tool-call syntax; retries burn latency and money.
**Mechanism.** Intersect the model's next-token distribution with a DFA/CFG of the target grammar at inference time; malformed output becomes unrepresentable (outlines, XGrammar, structured outputs APIs).
**Analysis.** Proven (structured outputs in all major inference stacks). Baseline-tier for estate agent tool calls (no named implementor yet; the clawdius association was wrong: raw completions, no schema constraint -- drift-check caught it, 2026-11-20). Refuse nowhere for schema-validated generation; it is strictly cheaper than retry loops.; (clawdius: n/a)
**Links.** P37 (repairs the residual semantic failures grammar cannot express); T49 (verification closes the loop).

### T49 · Stochastic generator + deterministic verifier loops
**Failure.** Trusting LLM output or generated code on plausibility; errors compound silently.
**Mechanism.** Cheap non-deterministic synthesis, then a rigorous deterministic verifier (typechecker, property tests, solver, test suite) gates acceptance; failures feed structured error context back to the generator.
**Analysis.** Proven (P vs NP asymmetry exploited everywhere: property-based testing, compiler-verified codegen, AlphaCode-style filtering). Baseline-tier for estate synthesis flows (scaffolds, codemods, agent outputs).
**Links.** X4 (spec-as-source is this pattern institutionalized as the module structure itself); A4 (metamorphic gates when no hard verifier exists).

### T50 · Schema-bound agentic capability sandboxes
**Failure.** Probabilistic agent loops mutate real systems on LLM judgment; one hallucinated parameter is a production incident.
**Mechanism.** Wrap the reasoning loop in a deterministic FSM: every external action passes schema validation, OCap permission checks (T8), and a deterministic rollback path before commit.
**Analysis.** Proven as architecture (every serious agent framework converges here); the pattern is the *invariant*, not a library. Baseline-tier for estate agents; clawdius is the reference implementor (capability-gated MCP gateway, SandboxLevel executor, Lean-verified invariants). bot-kit does not implement it (drift-check caught that association, 2026-11-20). Refuse nowhere for agents with write access.; (clawdius: adopted); (bot-kit: n/a)
**Links.** P31 (prompt quarantine feeds it clean inputs), P36 (CoW dry-runs are its staging tier), P40 (budget attenuation caps its reach), X6 (stopping rules bound its runtime).

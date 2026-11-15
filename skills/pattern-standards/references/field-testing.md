# Field VIII: Test Strategy (P64–P69)

Constructs that decide whether a test suite proves anything. Selection
rule: properties over generated inputs for pure cores (P64), builders
for fixtures (P68), golden masters for undocumented behavior (P65),
fuzzing for parsers (P67), mutation for measuring strength (P66),
quarantine for flakes (P69). Mock-heavy suites are refused (R2).

### P64 · Property-based testing
**Failure.** Example tests encode the cases the author imagined; the unimagined input class is where the bug lives.
**Mechanism.** Assert invariants over generated inputs with automatic shrinking: parse∘render roundtrips, conservation laws (P11: `Σ shares = total` for arbitrary weights), monotonicity, idempotence. A failing case shrinks to the minimal reproducer.
**Analysis.** Proven (QuickCheck 2000; Hypothesis, proptest, fast-check). Baseline for quant kernels and parsers in the estate. Refuse for thin glue where the invariant is the type signature.
**Links.** T49 (properties are the verifier), P15 (Finite<T> tested by generated operator storms), P68 (builders seed generators).

### P65 · Golden-master (approval/snapshot) testing
**Failure.** Legacy behavior is undocumented; refactoring has no spec to test against, so every change is blind.
**Mechanism.** Capture current output as an approved golden file; tests diff against it; diffs are reviewed and approved deliberately. The master is a characterization of what is, not what should be.
**Analysis.** Proven (ApprovalTests, Jest snapshots lineage). Adopt for legacy characterization and stable-format renderers. Refuse for new code: snapshotting today's bugs writes them into the spec (use P64 properties or P57 contracts instead).
**Links.** P57 (contracts for intended interfaces; goldens for inherited ones), P58 (strangler slices need characterization tests of the old path).

### P66 · Mutation testing
**Failure.** 90% line coverage with 10% assertion strength: tests execute code without asserting anything meaningful about it.
**Mechanism.** Mutate the code (flip comparisons, remove calls, off-by-one); every mutant that survives the suite marks assertions too weak to notice. Score mutants killed over mutants generated.
**Analysis.** Proven (PIT, mutmut, cargo-mutants). Run as a scheduled audit over changed modules, not per-commit (runtime cost). Refuse for untested code (write tests first, measure strength later).
**Links.** T49 (verifier strength measurement), P64 (properties typically kill the mutants examples miss).

### P67 · Structure-aware fuzzing
**Failure.** Hand-rolled parsers and protocol decoders crash or hang on inputs no example test ever imagined (truncated frames, hostile unicode, depth bombs).
**Mechanism.** Coverage-guided fuzzers (libFuzzer/AFL) drive generators that produce structurally valid-then-mutated inputs; the target must survive without panic, hang, or OOM; corpus and crashes are checked in.
**Analysis.** Proven (libFuzzer, cargo-fuzz, AFL++). Baseline for anything that parses untrusted bytes: webhook payloads (P54), file importers, protocol edges. Refuse for code without an input boundary.
**Links.** P37 (repair parsers are born from fuzz findings), T36 (deterministic replay of a found crash), P29 (fault shapes from fuzz corpora).

### P68 · Test-data builders
**Failure.** Fixtures are copy-pasted JSON blobs or one shared mutable "test user" that every test silently depends on; arrange phases are unreadable and order-dependent.
**Mechanism.** One builder per entity: valid by default, explicit overrides at the call site (`user(paid: true, tenant: acme)`); no shared mutable fixtures; deterministic seeds so builders feed generators (P64) unchanged.
**Analysis.** Proven (Object Mother/Builder lineage, xUnit Patterns). Refuse nowhere in typed estates; the cost is one small module per aggregate.
**Links.** T13 (pure cores make valid-by-default cheap), P64 (builders are the generator's frontend), P50 (synthetic data passes the same builders).

### P69 · Flaky-test quarantine + bisection
**Failure.** A flaky test trains the team to re-run CI until green; the suite's signal rots and real failures hide in the noise.
**Mechanism.** Flakes auto-quarantine with an expiry date (a P44 discipline for tests: quarantined means scheduled for fixing, not forgotten); root-cause via deterministic replay (seeded scheduler, T36) and commit bisection; quarantine depth is a tracked metric with a burn-down gate.
**Analysis.** Emerging-to-proven (Google-scale flaky tooling; the expiry discipline is the transferable part). Refuse nowhere for CI suites over ~50 tests; below that, fix flakes immediately.
**Links.** T36 (determinism is the cure), P44 (expiry enforcement mechanics), P30 (flight recorders capture the flaky window).

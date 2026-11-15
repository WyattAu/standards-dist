# Field XIV: Verification Discipline (P96–P99)

Constructs that raise the *strength* of verification, borrowed from
the compilers and certification worlds where "the tests passed" is not
a conclusion. Shared failure mode: verification that measures presence
of execution rather than correctness of behavior.

### P96 · Verify-every-layer (internal verifier sandwich)
**Failure.** Internal pipeline stages (compiler passes, transform steps, protocol handlers) trust their input shape; one misbehaving stage poisons everything downstream and the crash surfaces stages away from the bug.
**Mechanism.** Define an internal state model with a mechanical verifier; every stage boundary runs the verifier on its output; each stage is then correct relative to a checked contract, and faults localize to the first boundary that fails. Cost is one O(n) pass per stage.
**Analysis.** Proven (the LLVM IR verifier runs between passes in debug builds; rust-analyzer asserts parser invariants between phases). This is T1 generalized from the system edge to *every internal seam*. Refuse verifying in production hot loops: full verification in debug/test builds, sampled verification in prod.
**Links.** T1 (edge parse; internal verify), T30 (rewriting stages above a verified shape), T17 (query graphs re-verify via their input records), P29 (fault injection on top of verified seams).

### P97 · Auto-blessing golden masters
**Failure.** Golden-master suites rot: every intentional change invalidates hundreds of approved files, humans rubber-stamp re-approval in bulk, and real regressions hide inside the approval noise.
**Mechanism.** A tool regenerates expected output from the changed code and annotates each diff with the change that caused it; reviewers approve annotated regenerations in one review per intentional change. Review friction stays proportional to surprise, not to file count.
**Analysis.** Proven (LLVM's `update_test_checks.py` lineage; approval-testing tooling). Refuse auto-blessing without human review: that is deleting the test suite with extra steps.
**Links.** P65 (the underlying golden discipline), P57 (consumer contracts where contracts exist), P66 (mutation tells you whether the goldens would notice anything).

### P99 · Structural coverage gates (MC/DC)
**Failure.** Line coverage says a guard executed, not that its boolean structure was exercised; the one untested combination of conditions is exactly the case the incident rides in on.
**Mechanism.** For safety-critical or regulated modules, gate on modified condition/decision coverage: every atomic condition in every decision demonstrably affects the outcome independently; per-decision coverage matrices are CI artifacts; an uncovered combination requires a test or a documented waiver.
**Analysis.** Proven (DO-178C Level A requirement in avionics certification). Adopt for regulated and safety-critical modules; the cost is real and unjustified as an estate-wide default. Refuse MC/DC on CRUD glue; measure that with P66.
**Links.** P66 (mutation measures assertion strength; MC/DC measures decision structure; they find different holes), P64 (properties cover input classes; MC/DC covers decision structure), ADR-gated waivers per SPEC-CORE practice.

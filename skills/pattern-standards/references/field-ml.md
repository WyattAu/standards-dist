# Field XVII: ML Lifecycle (P111–P113)

Constructs for the path from training data to served model. Shared
failure mode: the offline world and the online world disagree, and the
disagreement is invisible until the metric has already moved.

### P111 · Train/serve skew guards
**Failure.** Features are computed one way in the training pipeline and another way online: different joins, different default fills, different time semantics. The model degrades silently, and nobody can say which change caused it.
**Mechanism.** Features are defined once (shared code or a registered spec) and materialized for both paths; parity tests replay production request features through the training transform and assert equality of values, defaults, and as-of semantics (P13); continuous skew metrics (P18 canaries) compare offline and online feature distributions.
**Analysis.** Proven ("training-serving skew" is canonical ML failure vocabulary; Uber Michelangelo and Google TFX practice). Refuse nowhere for online-served models; batch scoring inherits the same discipline through P110 contracts.
**Links.** P13 (as-of semantics cause most skew), P18 (the drift canary), P39 (memoization keys include the feature-spec version), P112 (skew gates are promotion criteria).

### P112 · Model registry + staged promotion
**Failure.** "Which model is in production?" is answered by asking whoever trained most recently; rollback means retraining; production weights live in someone's checkpoint folder.
**Mechanism.** Models are versioned artifacts, digest-addressed (P79 shape), held in a registry with stages: candidate, shadow, staged, production. Promotion moves a pointer and never rebuilds; serving loads by digest and records which digest answered each request (P42); rollback is a pointer revert measured in seconds.
**Analysis.** Proven (MLflow, SageMaker, Vertex model registries). Refuse registry-plus-vibes: a serving path that cannot state its model digest fails the pattern.
**Links.** P79 (the artifact discipline it inherits), P77 (the shadow stage is a dark launch), P111 (skew gates are promotion criteria), P39 (memoization keyed by model digest), P98 (dress rehearsal is the shadow-to-staged gate).

### P113 · Experiment bucketing + SRM checks
**Failure.** Assignment drifts (buckets recomputed differently across services or app versions), cohorts leak between arms, and the 50/50 split comes out 51/49; every downstream metric is now noise dressed as signal.
**Mechanism.** Assignment is a pure function: `hash(unit_id, experiment_salt) -> bucket`, stable across services and time; exposure is logged (P42) and continuously checked for sample-ratio mismatch, the cheapest valid-experiment alarm; guardrail metrics run alongside treatment metrics; stop conditions are pre-registered (R12 forbids free-form peeking).
**Analysis.** Proven (Microsoft ExP practice; doorkeeper-style bucketing; SRM alarms at every mature experiment platform). Refuse re-bucketing mid-experiment and daily metric reads without a sequential design (R12).
**Links.** P42 (exposure events), P44 (the flag that arms the experiment carries an expiry), P18 (guardrail drift canaries), P100 (experiment compute spends from a margin account).

# Field XI: Compliance & Privacy (P80–P86)

Constructs for the regulatory layer: consent, subject rights, purpose
limits, tamper-evidence, identity, and emergency access. The failure
mode they share is invisible non-compliance discovered during an audit
or an incident.

### P80 · Consent state machine
**Failure.** Consent is a nullable boolean on a user row; "may we email this person about X" is unanswerable, purpose drift is invisible, and withdrawal updates nothing downstream.
**Mechanism.** Consent is facts, not flags: append-only `(subject, purpose, granted|denied, timestamp, source)`; every processing path gates on a purpose query against the fact store; withdrawal propagates to processors as an event (T32) that must be acted on.
**Analysis.** Proven (GDPR consent doctrine). Refuse implied consent and purpose-wide blanket flags; both are the failure mode.
**Links.** T21 (the fact store), P43 (deletion is a key drop), P82 (purpose tags enforce collection scope).

### P81 · DSAR export pipeline
**Failure.** "Send me all my data" becomes a week of per-store archaeology; the assembled export misses a store and the miss is a regulatory finding, not a bug.
**Mechanism.** Subject-scoped export as a checkpointed job (the N20 shape): per-store collectors driven by the subject index (P43's key table is the index), assembled into a signed archive, delivered and audited with a jurisdictional SLO.
**Analysis.** Proven (GDPR Art. 15/20 practice). Refuse ad-hoc manual queries per request; a request type with an SLO is a pipeline, not a ticket.
**Links.** P43 (the key index finds every store), P56 (checkpointing), P60 (subject IDs), P83 (the export is audited).

### P82 · Purpose-limitation tagging
**Failure.** Data collected for billing quietly feeds analytics and model training; purpose creep is invisible until someone asks how a dataset was built.
**Mechanism.** Data carries purpose tags at write (column, table, or record level); queries declare the purpose they serve; the access layer enforces `declared purpose ⊆ collected purposes` structurally.
**Analysis.** Emerging (privacy-engineering stacks; the enforceable discipline is proven even where tooling is thin). Refuse where one purpose genuinely covers the dataset; do not tag theater.
**Links.** P41 (the same capability-binding shape on a purpose axis), P80 (the collected-purposes set comes from consent facts).

### P83 · Hash-chained audit log
**Failure.** Audit logs live in mutable stores; an administrator can edit history, and "who changed what, when" is unverifiable exactly when it matters.
**Mechanism.** Append-only entries; each carries `hash(previous)` plus its own content hash (certificate-transparency shape); the chain head is anchored externally or published periodically; verification walks the chain and fails on any gap.
**Analysis.** Proven (CT/Trillian lineage). Refuse nowhere for audit paths; the tuning knob is anchoring frequency.
**Links.** T21 (append-only substrate), T28 (the hashing discipline), auditlog (the estate implementation home), P86 (break-glass events land here).

### P84 · Workload identity
**Failure.** Services authenticate with static API keys in environment variables; a leaked key is unattributable, and rotation means downtime, so rotation never happens.
**Mechanism.** Every workload gets a platform-issued identity (SPIFFE, mTLS cert, instance identity); authentication is by identity, authorization by policy; static secrets remain only for external systems, brokered through a vault with an audit trail.
**Analysis.** Proven (SPIFFE/SPIRE; cloud IAM). Refuse nowhere for service-to-service auth; the migration order is internal first, external brokered second.
**Links.** T8 (identity is the capability substrate), P85 (rotation applies to what remains), P46 (network policy binds identities, not IPs).

### P85 · Zero-downtime secret rotation
**Failure.** Rotating a credential requires a coordinated deploy or accepts a crash window; rotations are deferred until the leak forces them.
**Mechanism.** Verifiers accept old and new during an overlap window; writers switch to the new secret first; the old is revoked after the window closes. Keys are versioned (P43 DEKs included); config epochs (P47) make the switch atomic per process.
**Analysis.** Proven (JWT `kid`, KMS rotation practice). Refuse nowhere; a secret without a rotation path is a standing incident.
**Links.** P43 (versioned DEKs), P84 (identity credentials rotate on the same schedule), P47 (epoch picks up the new secret atomically).

### P86 · Break-glass access
**Failure.** Real incidents need privileged access now; the approval flow cannot keep up, so teams keep standing admin credentials, which leak.
**Mechanism.** A pre-authorized emergency path: one request grants time-boxed elevated access, pages security immediately, records every action into the hash chain (P83), auto-revokes on expiry, and requires a post-incident review before the quota refills.
**Analysis.** Proven (SRE break-glass practice). Refuse standing admin credentials anywhere; they are the failure mode, not the fallback.
**Links.** P83 (the audit chain), P45 (the break-glass page is a P0), P27 (incident traffic outranks everything).

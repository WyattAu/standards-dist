# Field IX: API Surface (P70–P74)

Contracts for the outside edge of a service: how consumers tolerate
change, how errors read, how lists behave, and how deprecation happens
on a schedule instead of by ambush.

### P70 · Tolerant reader
**Failure.** A provider adds a field and every strict consumer breaks; or removes one and consumers that silently ignored it are fine while strict ones burn.
**Mechanism.** Consumers extract only the fields they need and ignore everything else (Postel-shaped, applied deliberately): unknown fields, unknown enum values routed to a documented default path. Producers may add freely; removal is the only breaking act.
**Analysis.** Proven (Fowler, "Tolerant Reader", 2006). Baseline for consumers outside your deploy unit. Refuse for internal same-monorepo calls where shared codegen (T6) already binds both sides exactly.
**Links.** P71 (the registry makes "added vs removed" mechanical), P1 (unknown-enum fallback paths are parse decisions).

### P71 · Schema registry with compatibility rules
**Failure.** Producers and consumers evolve schemas by hope; an incompatible change ships and consumers discover it by crash.
**Mechanism.** Schemas are registered artifacts with versions; the registry enforces a compatibility mode (default: backward: new schema reads old data) and rejects violations at publish time; messages carry schema IDs; consumers resolve explicitly.
**Analysis.** Proven (Confluent Schema Registry; Avro/Protobuf evolution rules). Adopt wherever event payloads (T32) or stored records outlive their code. Refuse for short-lived, single-deploy APIs where the type system is the registry.
**Links.** T32 (schema IDs ride the envelope), P57 (contracts test semantics; the registry governs shape), T48 (consumers validate at the parse boundary).

### P72 · Uniform error envelope
**Failure.** Every endpoint invents its own error shape; client error handling becomes per-endpoint archaeology and incident triage greps strings.
**Mechanism.** One stable error document (RFC 9457 `application/problem+json` shape): machine-readable code from a per-service registry, human detail, trace ID (P63), and retry semantics. Codes are never reused with new meaning; new cases add codes.
**Analysis.** Proven (RFC 9457; every mature API platform). Baseline for estate services. Refuse nowhere server-side; the design work is the code registry, and it is small.
**Links.** P63 (trace ID in the envelope), P42 (errors are wide events too), T1 (malformed requests parse into typed problems, not ad-hoc strings).

### P73 · Explicit list contract (filter/sort/page)
**Failure.** List endpoints accept arbitrary field filters (injection surface, unindexable queries), sort without tiebreaks (unstable pages), and paginate by offset (P7's failure mode).
**Mechanism.** Filterable and sortable fields are allowlisted; default sort is stable with a deterministic tiebreak; pagination is cursor-only (P7); unknown filter or sort parameters are 400, not silently ignored; sparse fieldsets optional.
**Analysis.** Proven (JSON:API and GraphQL conventions distilled). Baseline for estate list endpoints. Refuse for fixed small collections where a full payload is cheaper than the contract.
**Links.** P7 (the cursor discipline), S1 (tenant scoping is implicit in the allowlist, never a client-supplied filter), P72 (the 400s are typed problems).

### P74 · Deprecation protocol
**Failure.** Endpoints die by surprise removal, or never die: deprecated forever, consumers never migrate, the old path rots as a permanent liability.
**Mechanism.** Announce, then carry `Deprecation` and `Sunset` headers from announcement day; per-consumer usage telemetry identifies who still calls (from P42 wide events and P57 pacts); the removal date is public and enforced; expand-contract (add alongside, remove after the window).
**Analysis.** Proven (RFC 8594 Sunset; major platform practice). Adopt for any externally consumed API. Refuse for internal lockstep-upgraded callers: change them in the same commit (T6 codegen makes breakage a compile error).
**Links.** P1 (lenses carry old clients through the window), P44 (the removal date is a flag-expiry in disguise), P74 vs P58 (strangler moves traffic; deprecation retires it).

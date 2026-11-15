# Foundations I; Type-Level & Algebraic (T1–T10)

Moving invariants from runtime defensive checks and OOP indirection into
compile-time proofs and algebra. Maturity stamps: **Proven** (production
history), **Emerging** (real but thin adoption), **Speculative**.

### T1 · Parse, don't validate
**Failure.** Unverified boundary data re-enters checks at every layer; `if (x != null)` sprawls and drifts.
**Mechanism.** Transform boundary input once into proof-carrying types (`UserId`, `NonEmpty<T>`); interior code only accepts constructed values, so absence of a check is itself the proof.
**Analysis.** Proven (widespread Rust/Scala/TS idiom; Alexis King, "Parse, don't validate", 2019). Cost: newtype discipline at edges. Refuse when data never crosses a trust boundary; a parsed internal config is ceremony.
**Links.** T6 (HKD) generates the parsed/errored variants; P2 (constraint capsules) is this idea compiled to a shared artifact.

### T2 · Typestate / phantom state machines
**Failure.** Illegal protocol transitions (`read()` before `connect()`) are runtime panics or silent bugs.
**Mechanism.** Encode states as phantom parameters (`Conn<Authenticated> -> Conn<Open>`); methods consume the old state token and return the new one, making illegal transitions unrepresentable.
**Analysis.** Proven in Rust (e.g. `std::net::TcpStream` connect flow, database transaction handles). Cost: combinatorial state explosion if the graph is dense; keep to linear or tree protocols. Refuse for wide state graphs; use T46 (Datalog) or an FSM table instead.
**Links.** T7 (session types) generalizes this across processes.

### T3 · Tagless final
**Failure.** DSLs as AST data types hit the Expression Problem: adding an operation or variant forces edits everywhere.
**Mechanism.** Encode the DSL as a polymorphic interface (typeclass/trait) over an interpreter parameter `F<_>`; new operations and new interpretations are both additive.
**Analysis.** Proven in Scala/Haskell; practical in Rust with generics. Cost: type-inference friction and trait-bounds noise in TS-like languages. Refuse when the DSL has one interpreter and one consumer; a plain function is smaller.
**Links.** T4 (free monads) is the data-flavored alternative; pick one per codebase.

### T4 · Free / freer monads (programs as data)
**Failure.** Business logic is welded to effect execution; you cannot dry-run, log, or cost a program without mocks.
**Mechanism.** Reify imperative flow as a pure instruction tree; separate interpreters execute, dry-run, or trace the same tree.
**Analysis.** Proven but niche; interpreter boilerplate and allocation cost are real. Prefer T3 for compile-time erasure, T10 (algebraic effects) where the runtime has handlers, or T19 (durable coroutines) when the actual goal is replayability. Refuse as a default "architecture".
**Links.** T19 subsumes the replay use case with persistence.

### T5 · Functional optics (lenses, prisms, traversals)
**Failure.** Deep immutable updates become 10-line spread-and-map rituals; nested access breaks silently on schema change.
**Mechanism.** First-class composable bidirectional accessors over product/sum types; a traversal updates N focused locations in one composition.
**Analysis.** Proven (Haskell `lens`, Scala `Monocle`; TS via `monocle-ts`, Rust via `optic` crates). Cost: operator soup scares newcomers; constrain to a small DSL subset. Refuse in mutable-first code where direct field access already works.
**Links.** T6 (HKD) removes the need for optics over known record shapes.

### T6 · Higher-kinded data (HKD)
**Failure.** DTO duplication: `User`, `UserPatch`, `UserDraft`, `UserWithErrors` drift apart.
**Mechanism.** Parameterize one schema over a type constructor: `User<F>` instantiated as `User<Identity>`, `User<Partial>`, `User<Validation>`.
**Analysis.** Proven in Haskell/PureScript; Emerging in TS (mapped types carry it) and Rust (generic-associated types). Cost: HKT emulation friction outside ML-family languages. Refuse in languages without mapped types/GATs; codegen (OpenAPI/JSON-Schema-first) is the fallback.
**Links.** Feeds T1 and T5; the field series pursues the same one-schema-many-views goal at API boundaries (P1).

### T7 · Session types
**Failure.** Bidirectional protocols desynchronize: both sides wait, or one sends a message the other no longer accepts.
**Mechanism.** Encode the protocol (send/receive/branch/choice/close) in each endpoint's type; the type checker proves both parties implement dual views, so deadlock-by-desync is a compile error.
**Analysis.** Proven in research line (Multiparty Session Types, Honda et al.) and Emerging in practice (Rust `mpst` crates, F#, Scala runtime-checked variants). Cost: protocol changes ripple through types; that is the point, but budget for it. Refuse for simple request/response; HTTP already frames it.
**Links.** T2 (single-process version); X2 (choreographic programming) generates the projections automatically.

### T8 · Object-capability (OCap) attenuation
**Failure.** Ambient authority (`process.env`, global DB handles) means any dependency can do anything; audit is impossible.
**Mechanism.** Authority is an unforgeable reference; granting means passing a narrower reference. Attenuation composes: a file handle scoped to one path, a client scoped to one origin.
**Analysis.** Proven (E, Pony, Capsicum, WASI previews). Cost: threading capability parameters through call graphs; thread them explicitly or bundle them in builder records. Refuse nowhere in security-sensitive paths; adopt incrementally elsewhere.
**Links.** P46 (dependency manifests) applies OCap to third-party imports; P40 (spend leases) is OCap over budget; P41 (tenant tokens) is OCap over data.

### T9 · Defunctionalization
**Failure.** Higher-order closures make control flow unserializable and uninspectable; you cannot persist "what was about to happen".
**Mechanism.** Replace closures with a sum type of instructions plus one `apply` dispatch loop; the program's remaining work becomes inspectable, serializable data.
**Analysis.** Proven as a compiler technique (Reynolds 1972) and Emerging as an application pattern (interpreter loops, workflow engines' task lists). Cost: indirection. Adopt when serialization/replay of control flow is a requirement, else prefer T10.
**Links.** T19 (durable coroutines) is this plus persistence and deterministic replay.

### T10 · Algebraic effects & resumable handlers
**Failure.** Exceptions, DI, async, generators, and logging each use a different bespoke mechanism.
**Mechanism.** One primitive: perform a named operation, suspend, let a delimited handler decide; resume with a value, an exception, or a different result. DI becomes an effect; retry becomes a handler.
**Analysis.** Proven in OCaml 5, Koka, Eff, Unison abilities; Emerging elsewhere (JVM via Loom-adjacent work, JS via generators-as-effects). Cost: runtime/language support; do not emulate in TS. Refuse in languages without first-class support; use T3/T4.
**Links.** Unifies the interpretation concerns of T3, T4; pairs with T36 (deterministic schedulers) for reproducible effects.

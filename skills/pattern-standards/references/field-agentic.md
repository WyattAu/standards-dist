# Field IV — Probabilistic, AI & Agentic Engineering (P31–P40)

Constructs that make stochastic systems behave: quarantine inputs,
bound spend, verify outputs, and keep loops out of ditches. Baseline
surface for estate agents (clawdius, bot-kit, docs pipelines).

### P31 · Data-plane / control-plane prompt quarantine
**Failure.** Untrusted text from emails, PDFs, or DB rows hijacks agent tool calls via prompt injection.
**Mechanism.** Never interpolate untrusted strings into privileged planner prompts; untrusted inputs pass strictly as opaque `DataRef(#id)` handles consumed by isolated, non-privileged extractor steps.
**Analysis.** Proven direction (OWASP LLM risks; the dual-LLM pattern). Cost: an extractor sub-step per untrusted source. Baseline-tier for estate agents that read external content (crawlkit summaries, mail bots). Refuse nowhere in that class.
**Links.** T50 (the sandbox that enforces); T8 (handles as capabilities); P4 (sensitive-wrapper at the same boundary).

### P32 · Entropy-thresholded model cascading
**Failure.** Routing every query to a frontier model burns money and latency; small models hallucinate on hard cases.
**Mechanism.** Fast model first; inspect token-level entropy / top-2 margin at critical reasoning and tool tokens; escalate to the frontier model only on high-entropy spikes.
**Analysis.** Emerging-to-proven (cascade and routing literature; production adoption growing). Cost: logprob access (closed APIs restrict it) and threshold tuning per task. Adopt where logprobs are available and volume justifies it; refuse for low-volume interactive use where human latency dominates.
**Links.** X6 (cascade escalation is optimal stopping over models); P39 (memoization caches both tiers).

### P33 · State-hash trajectory loop breakers
**Failure.** Agents call the same failing tool with reworded arguments until the budget dies.
**Mechanism.** Hash normalized `(toolName, canonicalArgs, errorClass)` per step; a repeat hash forces context reset, strategy pivot, or deterministic escalation instead of another attempt.
**Analysis.** Proven as practice in agent frameworks (loop detection is table stakes); normalization depth is the engineering. Baseline-tier for estate agent loops. Refuse nowhere for tool-calling agents.
**Links.** X6 (stop-or-pivot is a stopping rule); P34 (metamorphic gates catch the *semantic* loops this misses).

### P34 · Metamorphic invariance eval gates
**Failure.** Unit tests cannot detect regressions when prompts, weights, or temperatures change; behavior drifts silently.
**Mechanism.** CI gates over metamorphic properties: semantic invariance under paraphrase, monotonicity under added evidence, statistical win-rate bounds against golden baselines.
**Analysis.** Emerging (metamorphic testing literature is solid; NLP application growing). Cost: eval-set curation and statistical patience. Adopt for estate prompt-pipelines with real blast radius (docs-pipeline extraction, trading summarization). Refuse for one-off scripts.
**Links.** T49 (hard verifiers when they exist; metamorphic when they don't); P36 (diff envelopes record which prompt version produced what).

### P35 · Prefix-pinned KV-cache layouts
**Failure.** Dynamic timestamps/UUIDs at the top of prompts bust the KV-cache every turn; inference pays full price per request.
**Mechanism.** Prompt assembly as immutable append-only prefix (`[static system+schemas] → [shared corpus] → [append-only turns]`); all volatile metadata goes to the trailing suffix.
**Analysis.** Proven (prompt caching is now a billed feature at every provider; layout discipline determines hit rate). Baseline-tier for estate multi-turn agents. Refuse nowhere; zero downside beyond rearranging prompt assembly.
**Links.** P39 (memoization at the API-call level; this at the model-state level).

### P36 · Staged copy-on-write diff envelopes
**Failure.** Agents mutate real DBs, calendars, and payment APIs; irreversible damage waits for one bad tool call.
**Mechanism.** Tool calls run against an ephemeral CoW sandbox first, compiling a deterministic dry-run diff (`+3 rows, -$120, 1 email`); policy or human approval commits atomically.
**Analysis.** Proven direction (plan-then-apply agent architectures; DB branching tools). Adopt for every estate agent with write access — no exceptions for "small" writes (refusal-class: unreviewed agent writes). Cost: sandbox fidelity per system touched.
**Links.** T50 (the enforcing shell); T31 (compensation for approved-but-wrong); P6 (parity checking against the sandbox).

### P37 · AST-guided minimal-edit repair parsers
**Failure.** Full LLM retries over trivial syntax errors (unclosed brace, fence, single quote) waste seconds and tokens.
**Mechanism.** Deterministic tree-repair parser ahead of schema validation fixes structural glitches in microseconds; generation retries only on genuine semantic violations.
**Analysis.** Proven components (JSON repair libs, error-tolerant IDE parsers) composed into a newer pattern. Adopt before every retry loop in estate agent pipelines. Refuse nowhere — strictly cheaper than re-generation.
**Links.** T48 (grammar constraints prevent most repairs from being needed); T49 (repair is the cheap verifier-adjacent fix).

### P38 · Hybrid symbolic-vector cache partitioning
**Failure.** Semantic caches return wrong answers when negations or dates flip meaning at 0.97 cosine similarity.
**Mechanism.** Partition the vector cache by cheap deterministic keys (`entities`, `negationFlags`, `timeBounds`, `tenantId`); nearest-neighbor lookup executes strictly inside the matching bucket.
**Analysis.** Emerging (GPTCache-lineage tooling plus hard lessons). Cost: key extraction per query. Adopt for estate semantic caching at volume; refuse when exact-match memoization (P39) covers the traffic.
**Links.** P39 (the exact sibling); P18 (distribution canaries guard cache-population quality).

### P39 · Content-addressed inference memoization
**Failure.** Multi-step pipelines fail at step 14 of 20; every debug run re-pays steps 1–13.
**Mechanism.** Key every LLM/embedding call on `hash(modelId, promptBytes, schemaHash, seed)` into an immutable local/S3 store; crashes and edits replay prior steps at zero cost.
**Analysis.** Proven (memoization is old; the inference-specific key discipline is the pattern). Baseline-tier for docs-pipeline and any multi-stage estate pipeline. Refuse for interactive single-turn calls.
**Links.** T28 (content addressing); P35 (prefix pinning for live calls); P38 (when approximations are acceptable, partition first).

### P40 · Attenuable spend-lease macaroons
**Failure.** Recursive sub-agent spawning runs up unbounded API bills with no global visibility.
**Mechanism.** Every call carries a cryptographically attenuated dollar/token lease; spawning a sub-agent carves a smaller sub-lease from the parent; exhaustion returns a typed `BudgetExhausted` fault cleanly at zero.
**Analysis.** Emerging (macaroons are proven; the spend application to agents is new practice). Adopt for estate multi-agent runs. Cost: a lease-issuing coordinator; worth it before, not after, the first runaway bill.
**Links.** T8 (OCap attenuation); P17 (risk-budget tokens — same shape over market exposure); X6 (stopping rules bound time as well as money).

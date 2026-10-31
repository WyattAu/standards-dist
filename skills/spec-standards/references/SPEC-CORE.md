# SPEC-CORE: the WyattAu specification and documentation contract

> **Status: CURRENT (v1.1.0, 2026-10-31).** Normative and living: changes
> require an ADR in `docs/adr/` and a version bump in the header plus
> `CHANGELOG.md`. Cited by gates as `SPEC-CORE §N`.

**Oracle:** No-oracle: normative process contract over documents, not
executable semantics. The oracle rule (SC-6) applies to specs that define
semantics, not to this contract.

## §1 Scope and boundary

SPEC-CORE governs how truth is written down (specifications) and
communicated (documentation) across the WyattAu estate.
[`engineering-standards`](https://github.com/WyattAu/engineering-standards)
governs how code is built, tested, and shipped (gate matrix, OMNI-CORE,
supply chain). The boundary:

| Concern | Owner |
|---|---|
| Code CI gates, tiers, security, supply chain, SBOM | engineering-standards (OMNI-CORE) |
| Spec invariants, truth tables, REQ anchors, spec lifecycle | spec-standards (this file) |
| Prose register, citation rule, character rules | spec-standards (`DOC-STYLE.md`) |
| Doc and spec gate scripts, registry schema | spec-standards (`scripts/`, §7) |
| REQUIREMENTS.md, THREAT-MODEL.md, SECURITY.md templates | engineering-standards `templates/` (referenced, never copied) |

Neither repository forks the other; each references (the invariant 11i
pattern applied to standards themselves). Violations of the boundary are
corrected by moving the artifact to its owner and leaving a pointer.

## §2 The ten invariants

| # | Invariant | Why |
|---|---|---|
| SC-1 | **One normative home per concern.** Every repo publishes a truth table (§3) mapping each normative concern to exactly one file. | Two files claiming one concern guarantees drift; the audit can only trust a unique address. |
| SC-2 | **Normative vs informative is marked; sections are numbered.** Gates, tests, and proofs cite `SPEC §N`, never prose paragraphs. | Citations must resolve mechanically (`doc-lint.sh`, `spec-audit.py` grep section headers). |
| SC-3 | **Every normative statement carries an enforcement citation**: theorem name, golden-vector set, gate name, or test name. Generalizes the DOC-STYLE citation rule to specs. | A spec claim nobody enforces is a wish (DOC-STYLE §3: unlinked claims are draft material). |
| SC-4 | **REQ traceability anchors.** Specs carry `REQ-<DOMAIN>-NNN` ids in a requirements table; public implementation items carry doc-comment tags citing their REQ; at tier S every REQ names at least one verifying test or theorem. | Traceability is the defense-grade spine already proven by `engineering-standards/specs/wire-kit.md`; the standard promotes it from per-kit practice to estate invariant. |
| SC-5 | **Spec lifecycle: DRAFT, REVIEW, CURRENT, FROZEN, SUPERSEDED.** Frozen specs are append-only and carry a freeze date; superseded specs carry a successor pointer; corrections are logged, not erased (§5). | Frozen artifacts (estate strategy and risk docs carry explicit freeze dates, e.g. "frozen 2026-10-30") must be distinguishable from living ones, or predictions scored at gates have no stable referent. |
| SC-6 | **Executable-oracle rule.** A spec that defines semantics (numeric, wire, algebra, schedule) ships an executable oracle (Lean definition, Python reference, vector generator) and cites it bidirectionally; committed golden vectors regenerate diff-clean. | Prose-only semantics specs rot against the code; the accounting-spec posting algebra and estate research repos' Lean oracles with golden-vector sets are the proven pattern. |
| SC-7 | **Registry of record.** Each repo's docs posture is declared in the estate registry (`docs:` block, §7) and audited by `scripts/spec-audit.py`; the audit fails when the registry and reality disagree. | The engineering standard works because `estate-audit.py` fails on lies; docs get the same discipline. |
| SC-8 | **External normative sources are vendored or stably linked.** A spec or doc may not cite an uncitable external document ("the D12 pipeline doc", "their data-protection chapter") without a stable URL or a vendored copy under `docs/refs/`. | First observed failure, recorded 2026-10-31 in an estate application repo: normative rules in a README cite documents outside git; under DOC-STYLE §3 those claims are draft material. |
| SC-9 | **Gates are mechanical and local-first.** `scripts/*` do the work; CI mirrors exactly those scripts (OMNI-CORE 1). Every gate in §9 runs from a shell with no secrets and no CI-only steps. | Local green implies CI green; anything else trains agents to bypass the gate. |
| SC-10 | **llms.txt is the projection, gated.** Where required (§8) `llms.txt` exists, contains no placeholders, mirrors truth-table links, and is regenerated when spec files change. | Invariant 11i applied to specs: every agent reads the same contract. |
| SC-11 | **Projection freshness**: packaged projections of this canon (agent skills, MCP servers, doc sites) declare their source rev, are rebuilt by CI from this repo, and a stale projection fails this repo's gate; projections reference and never fork (pairs with engineering-standards OMNI-CORE 11p). | llms.txt (SC-10) proved the pattern; skills and MCP multiply the drift surfaces, so staleness must fail loudly, not silently. |

## §3 Truth table

Canonical heading, exact text: `## Where the truth lives`. The table lives
in the repo's contract file (`AGENTS.md` when present, else `README.md`) as
a two-column table:

```markdown
## Where the truth lives

| Concern | File |
|---|---|
| Numeric semantics (normative) | docs/SPEC.md |
| Operations/sprints | docs/ROADMAP.md |
```

Rules:

1. Exactly one file per concern (SC-1); two rows naming the same concern is
   a gate failure.
2. The `File` column holds exactly one backticked path per row; the path
   must exist in the repo (gate: `doc-lint.sh`).
3. Reference shape: `templates/TRUTH-TABLE.md`; estate repos adopted under
   SC-7 maintain their own instance in the contract file.

## §4 REQ traceability anchors

1. Ids have the shape `REQ-<DOMAIN>-NNN` (example: `REQ-WIRE-001`), defined
   in the spec's requirements table.
2. The requirements table has columns `| REQ | Statement | Verified by |`;
   `Verified by` holds a theorem name, test name, or gate name.
3. Public implementation items carry a doc-comment tag citing their REQ:
   `/// [REQ-WIRE-001] Totality: no panic on hostile input`.
4. Cross-check: `doc-lint.sh --req-check` (mandatory advisory at tier S)
   extracts ids from specs and greps the tree; a REQ with no code tag, or a
   code tag with no REQ row, is reported. Blocking at tier S from
   2027-01-01.

## §5 Lifecycle and versioning

Header status line, one per spec file, exact forms:

```markdown
> **Status: DRAFT**
> **Status: REVIEW**
> **Status: CURRENT**
> **Status: FROZEN (2026-10-30).** Append-only; changes via superseding spec + ADR.
> **Status: SUPERSEDED by docs/SPEC-v3.md.**
```

Rules:

1. `FROZEN` requires an ISO date in the line (gate-enforced); content is
   append-only after freeze; corrections arrive as a new version whose
   header names the corrected items (precedent: estate spec headers that
   note "corrected invariants" per version).
2. `SUPERSEDED` requires `by <path>` (gate-enforced); the successor file
   must exist.
3. Every material change is logged twice: the spec header version note and
   one entry in `CHANGELOG.md` or `RESEARCH_LOG.md`.
4. Predictions and dated claims inside frozen docs are scored only at
   gates, never mid-sprint (estate ROADMAP prediction discipline).

## §6 Executable oracle

1. Applicability: any spec section defining semantics (numeric formats,
   wire codecs, algebra, schedules). Not applicable to process contracts;
   such files carry the line `No-oracle: <reason>`.
2. The spec carries a header line `**Oracle:** <path>` naming the oracle;
   the oracle's header comment names the spec file and section (§2).
3. Golden vectors are committed; regeneration is deterministic and
   `git diff` clean (precedents: `accounting-spec` Lean posting algebra
   with committed theorem discipline; estate research repos ship
   `lake exe golden` vector sets).
4. Tier S specs without an oracle line or an explicit `No-oracle:` line
   fail `doc-lint.sh`.

## §7 Estate registry schema

The registry of record remains
[`engineering-standards` `estate.yml`](https://github.com/WyattAu/engineering-standards/blob/main/estate.yml);
this repository owns the `docs:` block schema and the auditor. One optional
block per repo:

```yaml
repos:
  <repo>:
    docs:
      tier: s
      specs: [docs/SPEC.md]
      truth_table: AGENTS.md
      llms_txt: true
      status: current
      last_audit: "2026-10-31"
```

| Field | Type | Rules |
|---|---|---|
| `tier` | `s`, `k`, `a`, `d` | required; see §8 |
| `specs` | list of paths | repo-relative paths of normative spec files |
| `truth_table` | path | file containing the §3 heading |
| `llms_txt` | boolean | whether `llms.txt` is required |
| `status` | `current`, `draft`, `frozen`, `stale`, `superseded` | required |
| `last_audit` | ISO date | required; `spec-audit.py` flags repos audited more than 90 days ago |

`scripts/spec-audit.py --registry` validates the schema offline;
`--registry --remote` additionally verifies spec paths and `llms.txt`
existence against GitHub via `gh api`, and flags repos whose `pushed_at`
postdates `last_audit` (projection or posture went stale).

## §8 Tiers

| Tier | Repos | Rationale |
|---|---|---|
| **S** spec-heavy | accounting-spec, spec-standards itself, plus estate research repos | semantics governed by SC-3/4/6 |
| **K** library kits | the kit estate | public interfaces need REQ anchors and projections, not full oracles |
| **A** application/business | estate application repos | normative business rules in README/REQUIREMENTS need truth tables and citable external sources (SC-8) |
| **D** doc pipelines | homebite_docs and peers | the artifact is documents; build reproducibility and link rot dominate |

The per-tier blocking matrix of mechanical gates lives in
[`README.md`](README.md) (the gate matrix), mirroring the engineering
standards README convention.

## §9 Gate scripts

| Script | Checks | Dependencies |
|---|---|---|
| `scripts/doc-lint.sh [tier]` | em-dash rule, markdownlint (when installed), truth-table presence and path existence, llms.txt presence and placeholder gate, status-stamp well-formedness (§5), oracle line presence (§6), REQ cross-check (`--req-check`) | POSIX shell, coreutils; markdownlint/npx optional |
| `scripts/spec-audit.py --repo [dir]` | repo-mode audit: truth table, spec statuses, oracle lines, llms freshness via git timestamps | python3 + git |
| `scripts/spec-audit.py --registry file [--remote]` | registry schema (§7); remote existence and staleness via `gh` | python3, PyYAML, gh (remote only) |

CI consumes only these scripts
(`.github/workflows/docs.yml`, tier input). No gate exists only in CI
(SC-9).

## §10 llms.txt projection

1. Format: the llms.txt convention already used across the estate
   (title, one-paragraph summary, bulleted links to normative files).
2. Gate: file exists where §8 requires it; `grep -E 'TODO|PLACEHOLDER|TBD|FIXME'`
   must be empty; every truth-table path appears as a link target.
3. Regeneration is part of any spec-file change; `spec-audit.py --repo`
   flags a projection whose last git commit predates the newest spec commit
   (advisory until 2027-01-01, then blocking at tiers S and K).

## §11 Projections of this canon

1. `llms.txt` (SC-10) is the in-repo projection; packaged skills and the
   standards MCP server (built in `standards-dist`) are off-repo
   projections (SC-11).
2. Every projection pins its source rev in a provenance file and is
   regenerated by the canon's CI; a projection whose rev is behind
   `main` fails this repository's gate.
3. Projections reference; they never fork. Repair is always: fix the
   canon, rebuild the projection.

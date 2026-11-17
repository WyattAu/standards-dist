# CONTEXT-CORE: the standard for information fed to LLMs

Status: CURRENT, 2026-11. 14 rules, 4 refusals, a 4-layer budget model,
and the estate standards-map. Projection source for the
`wyattau-context` skill (standards-dist).

## 1. Doctrine

Context is a budget measured in tokens, and every token fed to a model
is a claim: that it is current, that it is load-bearing, and that it
is the cheapest form of itself. Information enters a model through
exactly four layers; each layer has a format, a hard budget, and a
mechanical gate. Feeding is a routing problem solved by scripts, not a
dump solved by hope. Anything an agent needs repeatedly becomes a
script output; anything it needs once stays in a file it opens then.

## 2. Layers and budgets

| Layer | Artifact | Budget | Gate |
|---|---|---|---|
| L0 always-on | AGENTS.md per repo | <= 150 words, facts and pointers only | review + voice-lint |
| L1 retrieval key | skill descriptions, MCP tool descriptions | <= 500 chars, triggers + scope limits | skill_audit / description check |
| L2 on-trigger | SKILL.md body | 400-900 words, router + decision tables | skill_audit |
| L3 on-demand | references/, llms.txt | <= 3000 words per file | check-canon / audit |
| L4 computed | route/audit/triage script output | ~100 tokens per call | exit codes + tests |

Rules per layer live in `references/artifact-formats.md`; the routing
contract every canon's router implements is
`references/routing-contract.md`.

## 3. Rules

| Id | Rule | Why | Gate |
|---|---|---|---|
| CX-1 | Information enters at the lowest layer that answers it; promotion to a higher layer requires usage evidence | always-on tokens are paid on every turn | review |
| CX-2 | Every LLM-fed artifact is a pinned projection of a canon (SC-11); canon owns truth | hand-edited projections lie about freshness | build.sh --check |
| CX-3 | Every canon ships a task router implementing the routing contract (`references/routing-contract.md`) | deterministic computation is a script, not prose | canon Makefile |
| CX-4 | Cross-referenced IDs resolve mechanically | dead IDs are stale-context seeds | check-canon / canon gates |
| CX-5 | Counts stated in prose (patterns, techniques, nodes, refusals) are claims verified by a gate | stale counts mislead retrieval and humans alike | check-canon |
| CX-6 | The prose register is PRESENT/DOC-STYLE: tables over prose, verdict first, no em-dash, no fillers | register violations compound across every fed token | voice-lint --strict |
| CX-7 | MCP tool descriptions are prompts: what it does, triggers, and "Does not:" scope limits | descriptions are retrieval keys, not documentation | skill_audit / review |
| CX-8 | Never-feed list (see §5) is enforced, not advised | one secret or stale dump poisons the whole budget | scripts + review |
| CX-9 | Freshness is mechanical: projections carry canon rev + rebuilt stamp; staleness fails the build check | stale context is worse than missing context | build.sh --check |
| CX-10 | Over budget, shed in this order: L3 references by ID distance, then L2 elaboration, then L1 verbosity; never shed an M (mandatory) set | mandatory invariants are the floor | review |
| CX-11 | Ambiguity routes to the user: routers exit 1 with candidates and the union rule, never a silent guess | wrong-node answers are confidently wrong | routing-contract tests |
| CX-12 | Budgets are enforced by scripts (skill_audit, check-canon, voice-lint), not review vibes | advisory budgets are wishes | canon Makefiles |
| CX-13 | Every fed artifact carries provenance: canon + rev (PROVENANCE.yml, SC-11) | unversioned context cannot be refreshed or trusted | PROVENANCE files |
| CX-14 | llms.txt exists per canon: title, one-paragraph summary, link list; regenerated when structure changes | machine-facing table of contents is the cheapest L0 for crawlers and agents | canon AGENTS rules |

## 4. The estate standards-map

Which canon governs, its normative file, its deterministic router, and
its gate. The MCP `standards_route` tool is generated from this table.

| Canon | Normative file | Router (task -> answer) | Gate |
|---|---|---|---|
| pattern-standards | PATTERN-CORE.md + references/ | `scripts/route.py --task` (31-node graph) | `make ci` = voice-lint + check-canon |
| seo-standards | SEO-CORE.md + references/ | `scripts/route.py --task` (technique match) | `make ci` = voice-lint + catalog parse |
| spec-standards | SPEC-CORE.md + DOC-STYLE.md | `scripts/doc-triage.py --repo` (fact router) | `make ci` = doc-lint + spec-audit |
| engineering-standards | OMNI-CORE.md + scripts/ | `scripts/tier-route.py --traits` (fact router) | estate-audit + check-* library |
| standards (L0) | STANDARDS-CORE.md + standards/* | voice-lint (prose register) | standards-audit.py |
| context-standards | CONTEXT-CORE.md (this file) | this canon is the routing standard | voice-lint + skill_audit + context-audit |

Fact routers (spec, engineering) answer from repo facts and are
keyword-hinted, not auto-run, when the task carries no repo path.

## 5. Never-feed list

| Refusal | Instead |
|---|---|
| Full-file dumps presented as "context" | route outputs and selective reference loads |
| Hand-edited projections | edit the canon, rerun build.sh (SC-11) |
| Skills used as documentation | anything over budget is references/ behind a router |
| Unversioned context artifacts | PROVENANCE.yml with canon rev |
| Secrets in any fed artifact | key-files read at spawn (estate-keys); CX-8 |
| Vendor licenses, lockfiles, generated logs in skill references | point to the canonical source file |

## 6. Adoption

1. New canon: adopt CX-1..CX-14 in its AGENTS.md, ship a router per
   CX-3 when it has a catalog, register in the standards-map table
   above and in engineering-standards estate.yml.
2. New projection (skill/MCP tool): frontmatter per skill-forge, rev
   pin per SC-11, budget check per skill_audit.
3. Estate-wide CX enforcement: `scripts/context-audit.py --adoption`
   (context-audit) walks the standards repos + skills; run it before
   flippy changes. `wyattau-context` (the dist skill) is the entry
   point: load it when writing or editing any LLM-fed artifact.

## 7. Maintenance

Structure changes to this canon regenerate llms.txt and the dist
projection in the same commit. Rule additions need a CHANGELOG entry;
layer-model changes need an ADR.

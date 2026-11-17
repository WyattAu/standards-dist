---
name: wyattau-context
description: |
  The WyattAu standard for information fed to LLMs: a 4-layer budget
  model (L0 always-on AGENTS.md through L4 computed script output), 14
  CX rules, a never-feed list, the routing contract every canon router
  implements, and the estate standards-map. Use when writing or editing
  any LLM-fed artifact (AGENTS.md, SKILL.md, skill or MCP tool
  descriptions, llms.txt, route scripts), or when founding a canon or
  projection. Does not: debugging, pattern selection, SEO.
allowed-tools: read, grep, bash
license: Apache-2.0
---

# wyattau-context

Canon: [`WyattAu/context-standards`](https://github.com/WyattAu/context-standards)
(CONTEXT-CORE.md); `references/` is a vendored projection
(PROVENANCE.yml, SC-11). Fix the canon, rebuild the projection.

## Doctrine

Context is a token budget; every fed token is a claim that it is
current, load-bearing, and the cheapest form of itself. Information
enters through four layers; each has a format, a hard budget, and a
mechanical gate. Feeding is a routing problem solved by scripts.

## Layers and budgets

| Layer | Artifact | Budget |
|---|---|---|
| L0 always-on | AGENTS.md | <= 150 words, facts and pointers |
| L1 retrieval key | skill/MCP descriptions | <= 500 chars, triggers + "Does not:" |
| L2 on-trigger | SKILL.md body | 400-900 words, router shape |
| L3 on-demand | references/, llms.txt | <= 3000 words per file |
| L4 computed | script/MCP output | ~100 tokens per call; authoritative |

## Rules (CONTEXT-CORE §3, condensed)

Lowest layer wins (CX-1). Projections are pinned, never hand-edited
(CX-2, SC-11). Every canon ships a router per the routing contract
(CX-3). IDs resolve and counts are gate-checked (CX-4, CX-5). PRESENT
register applies to every fed word (CX-6). Tool descriptions are
prompts with scope limits (CX-7). Freshness is mechanical (CX-9).
Over budget, shed L3 by ID distance, then L2 elaboration; never shed a
mandatory set (CX-10). Ambiguity asks the user (CX-11).

## Never-feed

Full-file dumps as context; hand-edited projections; skills used as
documentation; unversioned artifacts; secrets (key-files only); vendor
licenses and lockfiles. Full list: CONTEXT-CORE §5.

## Routing contract

Task routers: `--task`, prefix-scored keywords, exit 0 confident /
1 ambiguous-with-candidates / 2 usage; ambiguity names candidates and
states the union rule. Fact routers: answer from repo facts and state
the inference source. Full contract:
`references/routing-contract.md`.

## Estate audit

Run the estate-wide CX check from the skill itself:
`python3 scripts/context-audit.py --adoption` (walks the standards
repos: L0 budgets, never-feed, llms.txt, adoption declarations; exit 1
on violations, warnings advisory). Pass `--strict` to fail on budget
overruns too.

## Estate standards-map

Which canon governs, its router, its gate: CONTEXT-CORE §4. The MCP
`standards_route` tool is generated from that table; call it before
reading any canon.

| Canon | Router | Gate |
|---|---|---|
| pattern-standards | `scripts/route.py --task` | make ci (voice-lint + check-canon) |
| seo-standards | `scripts/route.py --task` | make ci |
| spec-standards | `scripts/doc-triage.py --repo` | doc-lint + spec-audit |
| engineering-standards | `scripts/tier-route.py --traits` | estate-audit + check-* library |
| standards (L0) | voice-lint | standards-audit.py |
| context-standards | this canon is the routing standard | voice-lint + skill_audit |

The MCP `standards_route` tool is generated from this table; call it
before reading any canon.

## Anti-patterns

- Always-on prose that can rot; put it behind a gate or a router.
- Descriptions without scope limits; two skills covering one trigger.
- Feeding vendor licenses, lockfiles, or generated logs.
- Quote counts from memory; the gate owns the numbers.

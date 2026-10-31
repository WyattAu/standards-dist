# PRESENT: presentable text standard

> **Status: CURRENT (v0.1.0, 2026-10-31)**

**Layer:** L2 · **Depends:** STANDARDS-CORE@^0.2, SPEC@^1 · **Date:** 2026-10-31

## Scope

Any estate text a human reads: documentation, READMEs, reports, PR and
commit descriptions, design documents, session summaries. Agent-to-human
speech inherits this and adds the density rules of AGENTSPEAK.

## Dependencies

Inherits SPEC: DOC-STYLE register (fact with citation, procedure, decision
with rejected alternative), citation rule, character rule; SPEC-CORE SC-3
(unlinked claims are draft material).

## Invariants

| Id | Statement | Why | Enforcement |
|---|---|---|---|
| PR-1 | The conclusion is the first sentence; evidence and reasoning follow | readers decide in the first line whether the rest is worth their time | review |
| PR-2 | One idea per paragraph; enumerable facts become tables; causal chains stay prose | tables scan, prose persuades; mixing both loses both | review |
| PR-3 | Headings are navigational: the heading states the content, never teases it | readers navigate by headings alone | review |
| PR-4 | Every fenced code block carries a language tag | untagged fences break highlighting and the lint | markdownlint (MD040) |
| PR-5 | Claims carry units, measurement method, and scope: "P99 under 5 ms at 10k req/s, criterion commit `abc`", not "fast" | a number without its measurement is an anecdote | DOC-STYLE register (inherited) |
| PR-6 | Filler patterns are banned (normative list enforced by `voice-lint.py`): `it is worth noting`, `in order to`, `essentially`, `basically`, `utilize`, `please note that` | they add tokens and subtract information; their replacements are always shorter and equal | `voice-lint.py` (strict in standards repos; dated window estate-wide) |
| PR-7 | Long documents open with a summary block: the state of the world in one table or one paragraph | the reader who stops after line one is still correctly informed | review |
| PR-8 | Hedging is replaced by the state marker: write the marker (`unverified`, `assumed`, `conflict`), never the hedge (`perhaps`, `it seems`, `I think`, `might be worth`) | hedges hide which claims carry evidence | `voice-lint.py` |

## Gates

`scripts/voice-lint.py` (in the standards canon): fence-aware scan for the
PR-6 filler list, PR-8 hedging list, and the em-dash rule. Default:
advisory. `--strict`: blocking. The standards repos run it strict on
themselves; estate-wide rollout follows the dated-window pattern
(advisory until a flip date is chosen with the first adoption wave).

## Grounding

`spec-standards` DOC-STYLE (register, citation, character rules: the
inherited spine), markdownlint MD040 findings from the OmniGo-template
docs run (2026-10-31: untagged fences were the advisory tail), and the
presentation conventions used across the estate's own standards repos.

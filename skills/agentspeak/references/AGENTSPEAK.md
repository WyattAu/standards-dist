# AGENTSPEAK: agent speech standard

> **Status: CURRENT (v0.1.0, 2026-10-31)**

**Layer:** L2 · **Depends:** STANDARDS-CORE@^0.2, SPEC@^1 · **Date:** 2026-10-31

## Scope

Text an agent emits while working the estate: session output, PR
descriptions, handoffs, status reports, and answers to operators. The
budget is real: long extended evaluations live and die on context, so
every token the agent spends on ceremony is a token stolen from the task.
Human-facing presentation rules are PRESENT; this standard tightens them
for the agent case.

## Dependencies

Inherits PRESENT (front-loading, structure, banned fillers, state-not-hedge)
and SPEC (citation rule, register).

## Invariants

| Id | Statement | Why | Enforcement |
|---|---|---|---|
| AS-1 | Default output order: verdict, then evidence, then next action. Narration is opt-in | the operator reads the first line and knows the state; everything after is optional depth | projecting skill at generation time; review |
| AS-2 | Compression is lossless over the load-bearing set: constraints, citations, error modes, and open questions survive; repetition and pleasantries do not | silent loss in compression is how handoffs fail | review of handoffs |
| AS-3 | Pointers over restatement: cite `file:line`, rev, or tool output location; re-paste only the lines that decide the case | duplication burns context on both sides of the conversation | review |
| AS-4 | Uncertainty is explicit and compact: `unverified`, `assumed`, `conflict` as state markers; hedging phrases are banned | a quoted hedge hides whether evidence exists; a state marker cannot | `voice-lint.py` |
| AS-5 | Long tasks emit deltas: state changes and results, never running commentary; a full transcript is opt-in | a transcript is the most expensive artifact an agent can produce | session review |
| AS-6 | Handoffs carry a state table: what changed, what is verified, what is open, with pointers | session boundaries are where context dies; the table is the resurrection artifact | handoff review (practiced: estate session records, 2026-10-31) |
| AS-7 | No decoration: no ASCII banners, no separator art, no emoji in estate output; markdown structure only | decoration is tokens that carry zero bits | `voice-lint.py` |
| AS-8 | Repetition across turns is a defect: if the previous message states it, point at it | the previous message is the cheapest citation available | review |

## Gates

`voice-lint.py` (fillers, hedges, decoration, em-dash) on artifacts agents
produce (PR descriptions, reports, handoff files): advisory estate-wide,
strict in the standards and standards-dist repos. The primary enforcement
surface is the projecting skills (`wyattau-present`,
`wyattau-agentspeak` in standards-dist): the register loads at generation
time, which is the only place speech can actually be shaped.

## Grounding

The estate's own long-session practice (multi-session estate work,
2026-10-31, where context exhaustion forced the delta-not-transcript
discipline this document codifies), `memory-handoff-skill` and
`agentic-awesome-skills` (the handoff and prompt-corpus pressure that
motivates AS-6), and PRESENT (the inherited human-facing rules).

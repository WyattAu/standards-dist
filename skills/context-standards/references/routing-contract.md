# Routing contract: the CLI every standards router implements

A router turns a task (or repo facts) into the governing rules without
prose archaeology. Four routers exist in the estate; this contract
keeps them interchangeable for callers (agents, MCP tools, humans).

## CLI contract

| Verb | Meaning |
|---|---|
| `--task "<text>"` | keyword-scored traversal of the canon's catalog/graph (task routers only) |
| `--node <ID>` / `--pillar <X>` / `--list` | direct lookup forms, canon-dependent |
| fact-router args (`--repo`, `--traits`, `--lang`, `--crate`) | fact routers answer from repo facts, not task text |

## Output contract

- Exit 0: confident answer; stdout is the block (mandatory set, ask
  branches, refuse edges, or matching items). ~100 tokens target.
- Exit 1: ambiguous or no match; stdout lists candidates and states
  the union rule. The caller asks the user or reads the canon.
- Exit 2: usage error; stderr explains.

## Classification discipline (task routers)

- Keywords live in K lines (pattern canon) or the technique tables
  (SEO canon); matched with prefix scoring (stem-ish, min length 4).
- A zero score or a tie exits 1 with candidates; it never guesses.
- Multi-node tasks: union the mandatory sets, walk all ask chains;
  overlaps are consistent by design.

## Fact-router discipline (spec, engineering)

- Answer from repo facts (manifests, registry blocks, markers), never
  from task text; state the inference source ("advisory inference:
  SPEC*.md present") next to the answer.
- Delegating callers pass repo paths; a bare task yields keyword hints
  only.

## Current routers

| Canon | Script | Kind |
|---|---|---|
| pattern-standards | `scripts/route.py` (31-node K/M/A/R graph) | task |
| seo-standards | `scripts/route.py` (technique tables) | task |
| spec-standards | `scripts/doc-triage.py` (SPEC-CORE §7/§8) | fact |
| engineering-standards | `scripts/tier-route.py` (OMNI tiers + estate-tiers.json) | fact |

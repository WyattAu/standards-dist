# Artifact formats: the exact shapes of LLM-fed artifacts

Formats are contracts because scripts parse them. Where a budget lives
and who enforces it: CONTEXT-CORE §2.

## AGENTS.md (L0)

- <= 150 words; facts and pointers, no doctrine essays.
- Fixed sections when applicable: one-line canon pointer; "Where the
  truth lives" table (SC-1) when the repo declares a docs tier.
- Every line must be true next quarter; if a line can rot, it belongs
  in a gated reference instead.

## Skill description (L1)

- <= 500 chars: 1-2 sentences of what it does, explicit triggers
  ("Use when...", concrete nouns, error strings), then scope limits
  ("Does not: ...").
- This string is the retrieval key; vague descriptions are a retrieval
  bug, not a style issue. Enforced by `skill_audit.py`.

## SKILL.md (L2)

- 400-900 words (hard cap 2000). Router shape: canon pointer, decision
  tables ("read this when"), anti-patterns, scripts to call.
- Progressive disclosure: the body answers "should I load more, and
  which file"; detail lives in references/.
- Projected skills are never hand-edited (SC-11); SKILL.md wrappers are
  dist-owned and register-swept.

## MCP tool description (L1)

- Same contract as a skill description, in ~2 sentences: what it does,
  triggers, "Does not:". The inputSchema property descriptions are part
  of the prompt; write them for the model, not for a human API doc.

## llms.txt (L3)

- Title block ("> " summary of the canon: counts, series, router), then
  one "- [name](path): one-line contents" bullet per normative file.
- Regenerated whenever the canon structure changes (canon AGENTS rule).

## Route-script output (L4)

- Node/item ID line, M (mandatory) line, A (ask branches, in order),
  R (refuse edges), and the union-rule footer when relevant.
- Exit 0 confident, 1 ambiguous-with-candidates, 2 usage. Ambiguity
  names candidates and hands the decision to the user.

## Provenance (every layer)

- PROVENANCE.yml pins canon source, rev, vendored file list, rebuilt
  stamp. A fed artifact without provenance is unrefreshable and fails
  CX-13.

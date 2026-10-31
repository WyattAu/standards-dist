---
name: wyattau-present
description: |
  Present estate text rigorously and concisely per PRESENT: front-load the
  conclusion, tables for enumerable facts, prose for causal chains,
  navigational headings, language-tagged fences, measured claims with units
  and method, banned fillers, state markers instead of hedges, summary
  blocks on long documents. Load when writing or editing any estate
  document, README, report, PR description, or design doc.
allowed-tools: read, bash
license: Apache-2.0
---

# wyattau-present

Canon: [`WyattAu/standards`](https://github.com/WyattAu/standards)
(standards/PRESENT.md); `references/` is a vendored projection
(PROVENANCE.yml, SC-11).

## Decision rules

1. Verdict first sentence; evidence after (PR-1).
2. Enumerable facts become tables; causal chains stay prose (PR-2).
3. Headings state content; never tease (PR-3).
4. Claims carry units, method, scope (PR-5); anything else is draft
   material (SC-3).
5. Fillers and hedges are banned lists, not vibes: `voice-lint.py` in the
   canon repo is the normative list; state markers replace hedges (PR-8).
6. Long documents open with the state of the world (PR-7).

## Procedure

Run `bash <standards-dist>/scripts/voice-lint.py --strict <files>` before
pushing any document under the register.

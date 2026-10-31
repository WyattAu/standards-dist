---
name: wyattau-spec-standards
description: |
  Write and adopt WyattAu specifications and documentation per SPEC-CORE:
  authoring SPEC.md with numbered normative sections, status stamps
  (DRAFT/REVIEW/CURRENT/FROZEN/SUPERSEDED), truth tables ("Where the truth
  lives"), REQ traceability anchors, executable-oracle lines, llms.txt
  projections; adopting the shared docs gate at tier s/k/a/d; diagnosing
  doc-lint or spec-audit failures (em-dash rule, missing truth table,
  placeholder projections, stale stamps); running estate sweeps. Load when
  creating a repo, writing or reviewing a spec, wiring the docs workflow,
  or fixing a docs CI failure in the WyattAu estate.
allowed-tools: read, bash
license: Apache-2.0
---

# WyattAu spec-standards skill

The canon is [`WyattAu/spec-standards`](https://github.com/WyattAu/spec-standards);
`references/` here is a vendored projection (see PROVENANCE.yml). Repair is
always: fix the canon, rebuild the projection (SC-11).

## When to use

- Creating or scaffolding a WyattAu repo (docs gate + skeletons).
- Writing or reviewing a SPEC, truth table, ADR, or RESEARCH_LOG.
- A docs CI run failed and you need the failing gate decoded.
- Deciding a repo's tier (s/k/a/d) or graduating posture (draft/current).

## Decision rules

1. Tier: spec + oracle present → **s**; library kit → **k**; application
   with normative business rules → **a**; doc pipeline → **d**.
2. A normative statement without an enforcement citation (theorem, golden
   vector, gate, test) is draft material: do not ship it (SC-3).
3. Two files claiming one concern: pick the truest home, move, leave a
   pointer (SC-1). Never fork.
4. Frozen means append-only; corrections arrive as a new version whose
   header names the corrected items (SC-5).
5. Semantics without an executable oracle get `No-oracle: <reason>` or an
   oracle before merge at tier s (SC-6).
6. The em-dash character never appears in estate Markdown; replace with
   colon (headings), semicolon (body clauses), hyphen (bare/table cells).

## Procedures (run from the target repo)

- Full gate at your tier: `bash <skill-dir>/scripts/doc-lint.sh <tier>`
- Repo audit: `python3 <skill-dir>/scripts/spec-audit.py --repo . --tier <tier>`
- Registry audit: `python3 <skill-dir>/scripts/spec-audit.py --registry <estate.yml>`
- Adoption order: truth table into AGENTS.md → status stamps on normative
  docs → oracle line (tier s) → llms.txt → `docs.yml` workflow call →
  run the gate locally before pushing (SC-9).

## References

- references/SPEC-CORE.md: the eleven invariants, formats, registry schema
- references/DOC-STYLE.md: prose register, citation rule, character rule

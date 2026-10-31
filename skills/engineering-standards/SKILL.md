---
name: wyattau-engineering-standards
description: |
  Apply the WyattAu engineering standards (OMNI-CORE): scaffold a new repo
  from the Omni templates, choose the CI gate tier (A/B/C) and wire the
  shared rust-kit workflow, honor the twelve invariants (scripts canonical,
  Nix devShell, merge queue, agent-facing AGENTS.md/llms.txt, SBOM, formal
  verification, projection freshness), interpret estate-audit output
  (pin drift, coverage debt), and follow DOC-STYLE register/citation rules.
  Load when creating a repo in the WyattAu estate, wiring CI, publishing a
  crate, or answering "is this allowed by the estate contract".
allowed-tools: read, bash
license: Apache-2.0
---

# WyattAu engineering-standards skill

The canon is
[`WyattAu/engineering-standards`](https://github.com/WyattAu/engineering-standards)
(OMNI-CORE + gate matrix + estate.yml); `references/` here is a vendored
projection (see PROVENANCE.yml). Fix the canon, rebuild the projection.

## When to use

- Creating a repo or deriving from an Omni template.
- Choosing a CI tier or wiring the shared quality workflow.
- Deciding whether a practice violates the estate contract.
- Reading estate-audit findings (pin drift, coverage debt, staleness).

## Decision rules

1. Scripts are canonical; CI mirrors them. No CI-only steps, ever.
2. One Makefile verb set everywhere: `build test lint fmt fmt-check
   coverage contract ci`.
3. Tier A = latency-relevant or concurrency primitives (loom, miri, 90%
   cov); B = default kits; C = informational until the flip date.
4. AGENTS.md is the single contract per repo; CLAUDE.md and vendor files
   are pointers (11i); packaged skills are projections and go stale
   loudly (11p).
5. Registry status vocabulary is earned, not aspirational: `core` means a
   consumer suite pins you exactly (estate-audit enforces the claim).
6. Docs register and citation rules live in DOC-STYLE (references/);
   unlinked claims are draft material.

## Procedures

- New repo: derive from the Omni template (they now carry the docs gate
  and spec skeletons, ADR 0011), set area/status honestly, register in
  estate.yml, run `scripts/estate-audit.py`.
- Before publishing: cargo-deny, cargo-audit, semver-checks green; SBOM
  artifact attached; attestations on releases (11h/11j).
- Estate questions: run `scripts/estate-audit.py` in
  engineering-standards and read the three reports (drift, debt, dormant).

## References

- references/OMNI-CORE.md: the invariants (1..12 + 11f-11p), each with why
- references/DOC-STYLE.md: prose rules that apply to every doc you write

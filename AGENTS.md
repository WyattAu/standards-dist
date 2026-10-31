# AGENTS.md: standards-dist contract

Derived from the estate contract (engineering-standards) + SPEC-CORE
SC-11. This repo owns packaging, not truth.

1. Never hand-edit `skills/*/references/`, `skills/*/scripts/`, or
   `PROVENANCE.yml` pins: they are build products of `build.sh`.
2. Canon changes land in the canon repos first; this repo follows.
3. `build.sh --check` failing means a projection is stale; rebuild, do
   not re-pin by hand.
4. The MCP server is read-only. Mutation tools require an ADR and
   per-call confirmation design.

## Where the truth lives

| Concern | File |
|---|---|
| Spec + doc invariants | `skills/spec-standards/references/SPEC-CORE.md` (projection; canon: WyattAu/spec-standards) |
| Engineering invariants | `skills/engineering-standards/references/OMNI-CORE.md` (projection; canon: WyattAu/engineering-standards) |
| Packaging + freshness | `build.sh`, `PROVENANCE.yml` files |
| MCP tools | `mcp/standards_mcp.py` |

# standards-dist

Distributable projections of the WyattAu standards canons, per SPEC-CORE
SC-11 and OMNI-CORE 11p: this repo owns packaging only; the canons own
truth.

| Projection | Canon | Contents |
|---|---|---|
| `skills/spec-standards` | [spec-standards](https://github.com/WyattAu/spec-standards) | SPEC-CORE + DOC-STYLE references, the two gate scripts, adoption/authoring procedures |
| `skills/engineering-standards` | [engineering-standards](https://github.com/WyattAu/engineering-standards) | OMNI-CORE reference, scaffold/tier/audit procedures |
| `mcp/standards_mcp.py` | both | read-only MCP stdio server: doc_lint, spec_audit, conformance_checklist, estate_status |

## Install (skills)

OpenCode: copy `skills/<name>/` into `~/.config/opencode/skills/<name>/`
(or the project `.opencode/skills/`), then run `skillkit lint` if you want
the estate toolchain verdict. Claude: copy into `~/.claude/skills/<name>/`.

## Install (MCP)

```json
{ "mcpServers": { "standards": { "command": "python3",
  "args": ["/path/to/standards-dist/mcp/standards_mcp.py"] } } }
```

Read-only by design: checkers and checklists, no mutation tools.

## Freshness (SC-11 / 11p)

`PROVENANCE.yml` in each skill pins the canon rev. `build.sh` rebuilds
from canon checkouts (`SPEC_CANON`, `ENG_CANON` env or defaults);
`build.sh --check` exits 1 when a pin is behind `origin/main`. Canon CI
fails on stale projections; never hand-edit `references/` or `scripts/`.

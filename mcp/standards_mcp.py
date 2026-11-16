#!/usr/bin/env python3
"""standards-mcp: read-only MCP server exposing the WyattAu estate gates.

Thin adapter over the canonical scripts (SPEC-CORE SC-9: scripts are
canonical; this server only wraps them). Tools:

  doc_lint(path, tier)          run doc-lint.sh on a checkout
  spec_audit(path, tier)        run spec-audit.py --repo on a checkout
  conformance_checklist(path, tier)
                                missing-artifact worklist for a repo
  estate_status(registry_path)  validate a registry (estate.yml docs blocks)

Protocol: MCP stdio (JSON-RPC 2.0, newline-delimited). Zero dependencies.
Run: python3 standards_mcp.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent / "skills"
SPEC_SCRIPTS = SKILLS / "spec-standards" / "scripts"
PROTOCOL = "2025-06-18"

TOOLS = [
    {
        "name": "doc_lint",
        "description": "Run the WyattAu docs gate (doc-lint.sh) on a checkout at a tier. Blocking checks: em-dash rule, status stamps; tier-dependent: truth table, llms.txt, markdownlint, oracle lines. Returns the full gate output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Repo checkout path"},
                "tier": {"type": "string", "enum": ["s", "k", "a", "d"], "description": "Docs tier (SPEC-CORE 8)"},
            },
            "required": ["path", "tier"],
        },
    },
    {
        "name": "spec_audit",
        "description": "Run spec-audit.py --repo on a checkout: truth table, oracle lines, llms.txt presence/placeholders/freshness. Returns the audit output and verdict.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "tier": {"type": "string", "enum": ["s", "k", "a", "d"]},
            },
            "required": ["path", "tier"],
        },
    },
    {
        "name": "conformance_checklist",
        "description": "Return the concrete missing-artifact worklist for a repo to conform at a tier: truth table, llms.txt, status stamps, oracle line, docs workflow, registry block.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "tier": {"type": "string", "enum": ["s", "k", "a", "d"]},
            },
            "required": ["path", "tier"],
        },
    },
    {
        "name": "estate_status",
        "description": "Validate the docs blocks of a WyattAu estate registry file (estate.yml schema, SPEC-CORE 7). Schema-only offline; no network.",
        "inputSchema": {
            "type": "object",
            "properties": {"registry_path": {"type": "string"}},
            "required": ["registry_path"],
        },
    },
    {
        "name": "standards_route",
        "description": "Route a task to the governing WyattAu standards canon and its deterministic router script (patterns, SEO, spec tiers, CI tiers, prose register). Deterministic computation is a script, not prose.",
        "inputSchema": {
            "type": "object",
            "properties": {"task": {"type": "string", "description": "The task or question, in plain words"}},
            "required": ["task"],
        },
    },
]


def sh(cmd, cwd=None, timeout=300):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def tool_doc_lint(args):
    p = Path(args["path"]).resolve()
    r = sh(["bash", str(SPEC_SCRIPTS / "doc-lint.sh"), args["tier"]], cwd=p)
    return {"exit": r.returncode, "output": (r.stdout + r.stderr).strip()[-4000:]}


def tool_spec_audit(args):
    p = Path(args["path"]).resolve()
    r = sh([sys.executable, str(SPEC_SCRIPTS / "spec-audit.py"), "--repo", ".", "--tier", args["tier"]], cwd=p)
    return {"exit": r.returncode, "output": (r.stdout + r.stderr).strip()[-4000:]}


def tool_conformance_checklist(args):
    root = Path(args["path"]).resolve()
    tier = args["tier"]
    checks = []

    contract = root / "AGENTS.md"
    if not contract.exists():
        contract = root / "README.md"
    tt_ok = contract.exists() and "## Where the truth lives" in contract.read_text(encoding="utf-8", errors="replace")
    checks.append({"artifact": "truth table (SC-1)", "required": tier in ("s", "a"),
                   "ok": tt_ok, "how": "Add the '## Where the truth lives' table to AGENTS.md (templates/TRUTH-TABLE.md)"})

    llms = root / "llms.txt"
    checks.append({"artifact": "llms.txt projection (SC-10)", "required": tier in ("s", "a"),
                   "ok": llms.exists(), "how": "Write llms.txt: title, one-paragraph summary, links to normative files"})

    stamps_ok, stamp_file = True, ""
    for f in root.rglob("*.md"):
        if any(x in f.parts for x in (".git", "node_modules", "vendor", "dist")):
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").split("\n"):
            if "Status:" in line and "FROZEN" in line and not re.search(r"\d{4}-\d{2}-\d{2}", line):
                stamps_ok, stamp_file = False, str(f)
            if "Status:" in line and "SUPERSEDED" in line and " by " not in line:
                stamps_ok, stamp_file = False, str(f)
    checks.append({"artifact": "status stamps well-formed (SC-5)", "required": True,
                   "ok": stamps_ok, "how": f"Add ISO date to FROZEN / successor to SUPERSEDED ({stamp_file or 'none found'})"})

    oracle_ok = True
    if tier == "s":
        specs = [f for f in root.rglob("SPEC*.md") if not any(x in f.parts for x in (".git", "node_modules"))]
        for f in specs:
            body = f.read_text(encoding="utf-8", errors="replace")
            if "Oracle:" not in body and "No-oracle" not in body:
                oracle_ok = False
                checks.append({"artifact": f"oracle line in {f.name} (SC-6)", "required": True,
                               "ok": False, "how": "Add '**Oracle:** <path>' or 'No-oracle: <reason>'"})
    wf = root / ".github" / "workflows" / "docs.yml"
    checks.append({"artifact": "shared docs workflow (SC-9)", "required": True,
                   "ok": wf.exists(),
                   "how": "Add .github/workflows/docs.yml calling WyattAu/spec-standards/.github/workflows/docs.yml@main"})

    missing = [c for c in checks if c["required"] and not c["ok"]]
    return {"tier": tier, "conformant": not missing, "checks": checks,
            "missing_count": len(missing)}


def tool_estate_status(args):
    reg = Path(args["registry_path"]).resolve()
    try:
        import yaml  # type: ignore
    except ImportError:
        return {"error": "PyYAML required for registry mode (pip install pyyaml)"}
    data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
    repos = data.get("repos") or {}
    rows = []
    for name, entry in sorted(repos.items()):
        docs = (entry or {}).get("docs")
        if docs:
            rows.append({"repo": name, "tier": docs.get("tier"), "status": docs.get("status"),
                         "last_audit": docs.get("last_audit")})
    return {"repos_with_blocks": len(rows), "total_repos": len(repos), "blocks": rows}



ROUTE_TABLE = [
    # canon, checkout candidates, route script + base args, fallback keyword hints
    ("pattern-standards",
     ["~/dev/src/github.com/WyattAu/pattern-standards"],
     "scripts/route.py", ["--task"],
     {"pattern", "design", "architecture", "pagination", "idempotency", "cache",
      "deadline", "circuit", "webhook", "backfill", "experiment", "margin", "skew"}),
    ("seo-standards",
     ["~/dev/src/github.com/WyattAu/seo-standards"],
     "scripts/route.py", ["--task"],
     {"seo", "search", "ranking", "sitemap", "crawl", "serp", "structured data", "index"}),
    ("spec-standards",
     ["~/dev/src/spec-standards", "~/dev/src/github.com/WyattAu/spec-standards"],
     None, None,
     {"spec", "docs tier", "truth table", "doc lint", "llms.txt", "oracle", "status stamp"}),
    ("engineering-standards",
     ["~/dev/src/github.com/WyattAu/engineering-standards"],
     None, None,
     {"ci tier", "coverage", "loom", "miri", "crate layer", "release gate"}),
    ("standards",
     ["~/dev/src/standards"],
     None, None,
     {"prose", "voice", "em dash", "writing", "register"}),
]


def _stem(w: str) -> str:
    for suf in ("ing", "ion", "ies", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def tool_standards_route(args):
    """Route a task across the estate canons: delegate to each canon's
    router script where one exists (authoritative), fall back to keyword
    hints where the canon has no --task router. Deterministic computation
    is a script, not prose (skill-forge doctrine)."""
    import os
    task = (args.get("task") or "").strip()
    if not task:
        return {"error": "task required"}
    routes = []
    for canon, roots, script, base_args, hints in ROUTE_TABLE:
        words = {_stem(w) for w in re.findall(r"[a-z0-9]+", task.lower())}
        kw_hit = bool(words & {_stem(k) for k in hints})
        out_line = None
        for root in (roots if script else []):
            rp = Path(os.path.expanduser(root))
            sp = rp / script
            if not sp.is_file():
                continue
            argv = [sys.executable, str(sp)] + (base_args + [task] if base_args else [])
            r = sh(argv, cwd=str(rp), timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                out_line = ("canon-router", r.stdout.strip()[-1500:])
                break
            if r.returncode == 1 and kw_hit and r.stdout.strip():
                out_line = ("canon-router-ambiguous", r.stdout.strip()[-800:])
        if out_line:
            routes.append({"canon": canon, "source": out_line[0],
                           "script": f"{canon}/{script}", "output": out_line[1]})
        elif kw_hit:
            hint = f"{canon}/{script}" if script else f"{canon} (fact router: pass the repo path)"
            routes.append({"canon": canon, "source": "keyword hint", "run": hint})
    return {"task": task, "routes": routes,
            "note": "canon-router outputs are authoritative; keyword hints mean the canon has no task router for this question"}


HANDLERS = {
    "doc_lint": tool_doc_lint,
    "spec_audit": tool_spec_audit,
    "conformance_checklist": tool_conformance_checklist,
    "estate_status": tool_estate_status,
    "standards_route": tool_standards_route,
}


def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
            continue
        method = req.get("method", "")
        rid = req.get("id")
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": req.get("params", {}).get("protocolVersion", PROTOCOL),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "wyattau-standards-mcp", "version": "0.1.0"}}})
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name = req["params"]["name"]
            args = req.get("params", {}).get("arguments", {})
            try:
                result = {"content": [{"type": "text", "text": json.dumps(HANDLERS[name](args), indent=1)}]}
            except KeyError:
                result = {"isError": True, "content": [{"type": "text", "text": f"unknown tool {name}"}]}
            except Exception as e:
                result = {"isError": True, "content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}]}
            send({"jsonrpc": "2.0", "id": rid, "result": result})
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}})


if __name__ == "__main__":
    main()

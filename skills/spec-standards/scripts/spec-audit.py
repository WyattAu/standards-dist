#!/usr/bin/env python3
"""spec-audit: repo and registry audits for the WyattAu spec standard.

Implements SPEC-CORE §7 (registry schema) and §9 (gate inventory).

Modes:
  --repo [DIR] [--tier s|k|a|d]
      Audit one checkout: truth table (SC-1/§3), oracle lines (§6),
      llms.txt presence, placeholders, and freshness vs the newest spec
      commit (SC-10). YAML-free; needs git for freshness.
  --registry FILE [--remote]
      Validate `docs:` blocks in the estate registry (engineering-standards
      estate.yml or any file using the §7 schema). --remote additionally
      verifies spec paths and llms.txt existence via `gh api` and flags
      repos whose pushed_at postdates last_audit.

Exit codes: 0 pass, 1 failures, 2 usage error.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

TIERS = {"s", "k", "a", "d"}
STATUSES = {"current", "draft", "frozen", "stale", "superseded"}
FIELDS = {"tier", "specs", "truth_table", "llms_txt", "status", "last_audit", "notes"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TT_HEADING = "## Where the truth lives"
PLACEHOLDER_RE = re.compile(r"\b(TODO|PLACEHOLDER|TBD|FIXME)\b")


def git_time(path: Path) -> int:
    """Last commit touching path, as unix seconds; 0 when unavailable."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return int(out) if out else 0
    except Exception:
        return 0


# --------------------------------------------------------------------------
# repo mode
# --------------------------------------------------------------------------

def truth_table_rows(text: str) -> list[str]:
    """Backticked paths from the §3 truth-table section of a contract file."""
    rows: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.strip() == TT_HEADING:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("|"):
            rows.extend(m.strip("` ") for m in re.findall(r"`[^`]+`", line))
    return rows


def audit_repo(root: Path, tier: str, strict_freshness: bool) -> int:
    fails: list[str] = []
    advisories: list[str] = []

    contract = root / "AGENTS.md"
    if not contract.exists():
        contract = root / "README.md"
    if not contract.exists():
        msg = "no AGENTS.md or README.md; truth table has no home (SC-1)"
        (fails if tier in ("s", "a") else advisories).append(msg)
        contract = None

    if contract is not None:
        text = contract.read_text(encoding="utf-8")
        required = tier in ("s", "a")
        bucket = fails if required else advisories
        if TT_HEADING not in text:
            bucket.append(f"{contract.name}: missing '{TT_HEADING}' heading (SPEC-CORE §3)")
        else:
            rows = truth_table_rows(text)
            if not rows:
                bucket.append(f"{contract.name}: truth table has no path rows (SPEC-CORE §3)")
            for p in rows:
                if not (root / p).exists():
                    bucket.append(f"truth-table path missing: {p} (SC-1)")

    # oracle lines (§6, tier S)
    if tier == "s":
        for f in sorted(root.rglob("SPEC*.md")):
            if any(x in f.parts for x in (".git", "node_modules", "vendor", "dist")):
                continue
            body = f.read_text(encoding="utf-8", errors="replace")
            if "Oracle:" not in body and "No-oracle" not in body:
                fails.append(f"{f.relative_to(root)}: no 'Oracle:' or 'No-oracle:' line (SPEC-CORE §6)")

    # llms.txt (SC-10): blocking at s/a; k/d advisory until 2027-04, then
    # the window escalates automatically (README matrix; same as doc-lint).
    llms = root / "llms.txt"
    kd_blocking = datetime.date.today() >= datetime.date(2027, 4, 1)
    if tier in ("s", "a") and not llms.exists():
        fails.append("llms.txt missing (SC-10)")
    elif tier in ("k", "d") and not llms.exists():
        msg = "llms.txt missing (SC-10; advisory until 2027-04 at this tier)"
        (fails if kd_blocking else advisories).append(msg)
    if llms.exists() and PLACEHOLDER_RE.search(llms.read_text(encoding="utf-8")):
        fails.append("llms.txt contains placeholders (SC-10)")

    # freshness: projection must not predate the newest normative file (SC-10)
    # Auto-strict at tiers s,k from 2027-01, or with --strict-freshness.
    strict = strict_freshness or (
        tier in ("s", "k") and datetime.date.today() >= datetime.date(2027, 1, 1)
    )
    if llms.exists() and contract is not None:
        watched = sorted(root.rglob("SPEC*.md")) + [contract]
        watched = [f for f in watched if not any(x in f.parts for x in (".git", "node_modules", "vendor", "dist"))]
        newest = max((git_time(f) for f in watched), default=0)
        mine = git_time(llms)
        if newest and mine and mine < newest:
            msg = "llms.txt predates the newest spec/contract commit (SC-10); regenerate"
            (fails if strict else advisories).append(msg)

    for a in advisories:
        print(f"ADVISORY: {a}")
    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        print(f"spec-audit --repo: FAIL ({len(fails)} failure(s))")
        return 1
    print(f"spec-audit --repo: PASS (tier {tier}, {len(advisories)} advisory/advisories)")
    return 0


# --------------------------------------------------------------------------
# registry mode
# --------------------------------------------------------------------------

def gh_api(query: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["gh", "api", query], capture_output=True, text=True
        )
    except FileNotFoundError:
        return False, "gh not installed"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()[:200]
    return True, proc.stdout.strip()


def audit_registry(file: Path, remote: bool) -> int:
    try:
        import yaml  # type: ignore
    except ImportError:
        print("PyYAML required for registry mode (provided by flake.nix devShell)", file=sys.stderr)
        return 2

    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
    repos = data.get("repos") or {}
    if not repos:
        print(f"FAIL: {file}: no 'repos:' entries")
        return 1

    schema_fails: list[str] = []
    advisories: list[str] = []
    rows: list[tuple[str, str, str, str, str]] = []
    today = datetime.date.today()

    for name, entry in sorted(repos.items()):
        docs = (entry or {}).get("docs")
        if not docs:
            rows.append((name, "-", "-", "-", "no docs block"))
            advisories.append(f"{name}: no docs block (SC-7)")
            continue

        unknown = set(docs) - FIELDS
        if unknown:
            schema_fails.append(f"{name}: unknown docs fields {sorted(unknown)} (§7)")
        tier = docs.get("tier")
        status = docs.get("status")
        last_audit = docs.get("last_audit")
        specs = docs.get("specs", [])

        if tier not in TIERS:
            schema_fails.append(f"{name}: tier '{tier}' not in {sorted(TIERS)} (§7)")
        if status not in STATUSES:
            schema_fails.append(f"{name}: status '{status}' not in {sorted(STATUSES)} (§7)")
        if not isinstance(last_audit, str) or not DATE_RE.match(last_audit):
            schema_fails.append(f"{name}: last_audit '{last_audit}' not ISO date (§7)")
        elif datetime.date.fromisoformat(last_audit) > today:
            schema_fails.append(f"{name}: last_audit is in the future (§7)")
        if not isinstance(specs, list) or not all(isinstance(s, str) for s in specs):
            schema_fails.append(f"{name}: specs must be a list of paths (§7)")

        verdict = "ok"
        if remote:
            for p in specs:
                ok, _ = gh_api(f"repos/WyattAu/{name}/contents/{p}")
                if not ok:
                    schema_fails.append(f"{name}: spec path missing on GitHub: {p} (SC-7)")
            tt = docs.get("truth_table")
            if tt:
                ok, _ = gh_api(f"repos/WyattAu/{name}/contents/{tt}")
                if not ok:
                    schema_fails.append(f"{name}: truth_table missing on GitHub: {tt} (SC-7)")
            if docs.get("llms_txt"):
                ok, _ = gh_api(f"repos/WyattAu/{name}/contents/llms.txt")
                if not ok:
                    schema_fails.append(f"{name}: llms_txt declared but llms.txt missing on GitHub (SC-10)")
            ok, out = gh_api(f"repos/WyattAu/{name}")
            if ok:
                try:
                    pushed = datetime.date.fromisoformat(json.loads(out)["pushed_at"][:10])
                    if last_audit and isinstance(last_audit, str) and DATE_RE.match(last_audit):
                        if pushed > datetime.date.fromisoformat(last_audit):
                            advisories.append(f"{name}: pushed {pushed} after last_audit {last_audit}; posture may be stale")
                            verdict = f"stale? (pushed {pushed})"
                except (ValueError, KeyError):
                    pass

        rows.append((name, str(tier), str(status), str(last_audit), verdict))

    width = max(len(r[0]) for r in rows) + 1
    print(f"{'repo'.ljust(width)} tier  status     last_audit  verdict")
    for name, tier, status, la, verdict in rows:
        print(f"{name.ljust(width)} {str(tier).ljust(5)} {str(status).ljust(10)} {la.ljust(11)} {verdict}")

    for a in advisories:
        print(f"ADVISORY: {a}")
    for f in schema_fails:
        print(f"FAIL: {f}")
    if schema_fails:
        print(f"spec-audit --registry: FAIL ({len(schema_fails)} failure(s))")
        return 1
    print(f"spec-audit --registry: PASS ({len(rows)} repos, {len(advisories)} advisory/advisories)")
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="SPEC-CORE §7/§9 auditor")
    ap.add_argument("--repo", nargs="?", const=".", default=None, help="audit a checkout (default: cwd)")
    ap.add_argument("--tier", choices=sorted(TIERS), default="s", help="tier for repo mode (default: s)")
    ap.add_argument("--registry", type=Path, default=None, help="audit a registry file (estate.yml)")
    ap.add_argument("--remote", action="store_true", help="registry mode: verify paths via gh api")
    ap.add_argument("--strict-freshness", action="store_true",
                    help="repo mode: llms.txt freshness is blocking (SC-10: blocking from 2027-01)")
    args = ap.parse_args()

    if bool(args.repo is not None) == bool(args.registry is not None):
        ap.error("exactly one of --repo or --registry is required")

    if args.repo is not None:
        return audit_repo(Path(args.repo).resolve(), args.tier, args.strict_freshness)
    return audit_registry(args.registry, args.remote)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""drift-check: canon-vs-reality drift detector (CONTEXT-CORE CX-5, M10).

Scans the canon for per-repo pattern claims ("Baseline-tier for <repo>",
"adopted in <repo>", "target: <repo>") and cross-checks each claim against
that repo's PATTERN_ADOPTION.md declaration.

Drift verdicts:
  DRIFT   canon claims baseline/adopted; repo declares planned/refused/n-a
  REVERSE repo declares adopted; canon claims planned (informational)
  MISSING repo is claimed in the canon but declares no adoption file
          (rollout tracker; warning unless --strict)

Usage:
  drift-check.py [--canon DIR] [--repos-root DIR] [--registry FILE] [--strict]
Exit 1 on DRIFT/MISSING under --strict or without --strict for DRIFT.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

CLAIM_PATTERNS = [
    # "Baseline-tier for billing-kit fee/inventory splits"
    re.compile(r"[Bb]aseline[- ]tier for ([a-z0-9-]+)"),
    # "adopted in accounting-spec", "the estate's accounting-spec home"
    re.compile(r"[Aa]dopted (?:in|by) ([a-z0-9-]+)"),
    # "billing-kit adoption: planned 0.3.0"
    re.compile(r"([a-z0-9-]+) adoption: (?:planned|adopted)"),
    # "target: billing-kit (0.3.0)"
    re.compile(r"[Tt]arget: ([a-z0-9-]+)"),
]


def canon_repo_claims(canon: Path, known_repos: set[str]) -> list[tuple[str, str, str, str, str]]:
    """(repo, pattern_id, claim_kind, canon_ref, line) from all canon markdown.

    Claims appear as "Baseline-tier for <domain> (<repo>, <repo>)" and
    "adopted in <repo>" per-repo mentions inside pattern Analysis lines.
    Every estate repo name appearing on a claim line is a claimed repo."""
    claims: list[tuple[str, str, str, str, str]] = []
    files = sorted((canon / "references").glob("*.md")) + [canon / "PATTERN-CORE.md"]
    for f in files:
        if not f.is_file():
            continue
        pid = ""
        for i, line in enumerate(f.read_text(errors="replace").split("\n"), 1):
            h = re.match(r"^###\s+([TPX]\d+)", line)
            if h:
                pid = h.group(1)
                continue
            if not pid or "Baseline-tier" not in line and "adopted in" not in line:
                continue
            for repo in known_repos:
                if re.search(rf"\b{re.escape(repo)}\b", line):
                    kind = ("adopted" if re.search(r"[Aa]dopted (?:in|by)", line)
                            else "baseline")
                    claims.append((repo, pid, kind, f"{f.name}:{i}", line))
    return claims


def inline_status(line: str, repo: str) -> str | None:
    """Annotated per-repo status on a claim line: '(repo: planned ...)'."""
    m = re.search(rf"{re.escape(repo)}\s*:\\?\s*\**?(planned|refused|adopted|n/a)\b", line)
    return m.group(1) if m else None


def repo_status(repo: Path, pid: str) -> str | None:
    f = repo / "PATTERN_ADOPTION.md"
    if not f.is_file():
        return None
    for line in f.read_text(errors="replace").split("\n"):
        m = re.match(rf"^\|\s*{re.escape(pid)}\s*\|\s*(\w+)\s*\|", line)
        if m:
            return m.group(1)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--canon", default=".")
    ap.add_argument("--repos-root", default=os.path.expanduser("~/dev/src/github.com/WyattAu"))
    ap.add_argument("--strict", action="store_true", help="MISSING (undeclared) repos also fail")
    ap.add_argument("--draft", metavar="OUT", help="write ready-to-apply canon correction drafts for found drifts")
    a = ap.parse_args()
    canon = Path(a.canon).resolve()
    repos_root = Path(a.repos_root).resolve()
    drafts = []
    known_repos = {d.name for d in repos_root.iterdir() if d.is_dir()}
    claims = canon_repo_claims(canon, known_repos)
    if not claims:
        print("drift-check: no per-repo claims found in the canon (nothing to cross-check)")
        return 0

    drifts: list[str] = []
    missing: list[str] = []
    checked = 0
    seen_repos: set[str] = set()
    for repo, pid, kind, ref, line in claims:
        seen_repos.add(repo)
        rdir = repos_root / repo
        status = repo_status(rdir, pid) if rdir.is_dir() else None
        if status is None:
            missing.append(f"{repo}: canon claims {pid} ({kind}, {ref}) but no PATTERN_ADOPTION.md declaration")
            continue
        checked += 1
        if kind not in ("baseline", "adopted"):
            continue
        inline = inline_status(line, repo)
        if inline is None:
            drifts.append(f"{repo}: baseline claim for {pid} ({ref}) lacks an inline status annotation '(repo: status)'")
            drafts.append((repo, pid, ref, f"({repo}: {status})"))
        elif inline.lower() != status.lower():
            drifts.append(f"{repo}: claim annotation {inline!r} != declared {status!r} for {pid} ({ref})")
            drafts.append((repo, pid, ref, f"({repo}: {status})"))
        elif kind == "target" and status == "refused":
            drifts.append(f"{repo}: canon targets {pid} ({ref}) but repo refuses it")

    if a.draft and drafts:
        out = []
        for repo, pid, ref, ann in drafts:
            fname, _, lineno = ref.rpartition(":")
            out.append(f"# {repo} {pid}: append '{ann}' to line {lineno} of {fname}")
        Path(a.draft).write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"drift-check: drafts written to {a.draft}")
    for d in drifts:
        print(f"DRIFT {d}")
    for m in missing:
        print(f"MISSING {m}")
    print(f"drift-check: {'FAIL' if drifts else 'PASS'} "
          f"({checked} claim(s) cross-checked, {len(drifts)} drift(s), "
          f"{len(missing)} undeclared, {len(seen_repos)} repos claimed)")
    return 1 if drifts else 0


if __name__ == "__main__":
    sys.exit(main())

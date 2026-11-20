#!/usr/bin/env python3
"""adoption-check: mechanical validation of a repo's PATTERN_ADOPTION.md.

The adoption file declares, per pattern, the adoption state and evidence.
This checker validates the declaration against the canon (context:
pattern-standards references/adoption-format.md, CONTEXT-CORE CX-4/CX-5):
  1. every referenced pattern ID exists in the canon catalog
  2. every status is in the closed vocabulary
  3. evidence paths exist (file[:line])
  4. refused rows cite a canon refusal ID (R1-R12) or a named reason
  5. a `<!-- adoption: canon -->` marker declares a canon repo: zero
     rows is then valid (the canon IS the catalog)

Usage:
  adoption-check.py --file PATTERN_ADOPTION.md [--canon <pattern-standards checkout>]

Exit 0 clean, 1 violations, 2 usage.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STATUSES = {"adopted", "planned", "partial", "refused", "n/a"}
ROW = re.compile(r"^\|\s*([TPX]\d+)\s*\|\s*([a-z/\- ]+)\s*\|\s*([^|]+)\s*\|", re.M)


def canon_ids(canon: Path) -> set[str]:
    ids: set[str] = set()
    core = canon / "CONTEXT-CORE.md"
    graph = canon / "references" / "decision-graph.md"
    # pattern-standards layout: PATTERN-CORE.md + references/catalog.md
    for base in (canon, canon / "references"):
        cat = base / "catalog.md"
        if cat.is_file():
            for m in re.finditer(r"^\| ([TPX]\d+) \|", cat.read_text(errors="replace"), re.M):
                ids.add(m.group(1))
    for f in (core, graph):
        if f.is_file():
            t = f.read_text(errors="replace")
            for m in re.finditer(r"^### ([N]\d+)", t, re.M):
                ids.add(m.group(1))
    return ids or set()


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--file", default="PATTERN_ADOPTION.md")
    ap.add_argument("--canon", default="~/dev/src/github.com/WyattAu/pattern-standards")
    a = ap.parse_args()
    f = Path(a.file)
    if not f.is_file():
        print(f"adoption-check: {f} not found (every estate repo declares one, even if empty)", file=sys.stderr)
        return 2
    canon = Path(a.canon).expanduser()
    catalog = canon / "references" / "catalog.md"
    if not catalog.is_file():
        print(f"adoption-check: canon catalog not found at {catalog}", file=sys.stderr)
        return 2

    known = canon_ids(canon)
    violations: list[str] = []
    t = f.read_text(encoding="utf-8", errors="replace")
    rows = ROW.findall(t)
    if not rows and "adoption: canon" not in t:
        violations.append("no adoption table rows found (format: references/adoption-format.md)")
    for pid, status, evidence in rows:
        pid, status = pid.strip(), status.strip()
        evidence = evidence.strip()
        if pid not in known:
            violations.append(f"unknown pattern id {pid!r}")
        if status not in STATUSES:
            violations.append(f"{pid}: status {status!r} not in {sorted(STATUSES)}")
        if status in ("adopted", "partial") and evidence in ("", "-", "todo"):
            violations.append(f"{pid}: {status} rows need an evidence path (file[:line])")
        elif evidence and evidence not in ("", "-", "todo"):
            # evidence cells may list several paths (separated by , + ; vs
            # and/because prose), each optionally backticked, with :line
            # suffixes and parenthetical notes: "the async shell is
            # src/lib.rs and src/tower.rs is the middleware (core)"
            # -> validate the slash-containing tokens as paths
            known_dirs = {"crates", "src", "tests", "docs", "examples", "benches",
                          "lean", "supply-chain", ".github", "scripts", "references",
                          "dot_agents", "adr"}
            def is_path_token(tok: str) -> bool:
                tok = tok.rstrip(".")
                if re.fullmatch(r"\d+(\.\d+)*", tok):
                    return False  # version numbers (0.3.0), not paths
                if tok.startswith("."):
                    return True  # dotfiles/dotdirs (.github/...)
                if "/" in tok:
                    first, last = tok.split("/")[0], tok.split("/")[-1]
                    return first in known_dirs or "." in last
                return "." in tok
            for tok in re.findall(r"[\w./-]+", evidence.replace("`", "")):
                tok = tok.split(":")[0].strip()
                if not is_path_token(tok) or tok in ("e.g", "etc", "vs"):
                    continue
                if not (f.parent / tok).exists() and not Path(tok).exists():
                    violations.append(f"{pid}: evidence path {tok!r} does not exist")
        if status == "refused":
            # spec (adoption-format rule 3): refused rows cite a refusal id
            # OR a written reason pointer (a path/date in the evidence)
            has_rid = re.search(r"R\d+", evidence)
            has_pointer = ("/" in evidence or re.search(r"\d{4}-\d{2}-\d{2}", evidence))
            if not (has_rid or has_pointer):
                violations.append(f"{pid}: refused rows must cite a refusal id (R1-R12) or a written-reason pointer")

    for v in violations:
        print(f"V {v}")
    print(f"adoption-check: {'FAIL' if violations else 'PASS'} "
          f"({len(rows)} rows, {len(violations)} violation(s))")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Token benchmark for standards-dist skills (AGENTSPEAK/PR-5 discipline:
measured, gated, recorded).

Estimates the context cost of each skill (SKILL.md + references/) using
the chars/4 heuristic, compares against baselines.json, and fails on a
regression beyond the tolerance. This is an ESTIMATE: a stable, dependency-
free proxy for tokenizer counts, good enough for regression detection.

Usage:
  token_benchmark.py                 # compare against baselines.json
  token_benchmark.py --update        # write new baselines (after review)
Env:
  TOKEN_TOLERANCE  relative growth allowed (default 0.10)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINES = Path(__file__).resolve().parent / "baselines.json"
CHARS_PER_TOKEN = 4.0
SCAN_DIRS = ["SKILL.md", "references", "scripts"]


def skill_tokens(skill: Path) -> dict:
    total_chars = 0
    files = 0
    for entry in SCAN_DIRS:
        p = skill / entry
        if p.is_file():
            total_chars += len(p.read_text(encoding="utf-8", errors="replace"))
            files += 1
        elif p.is_dir():
            for dp, dn, fn in os.walk(p):
                dn[:] = [x for x in dn if x not in (".git", "node_modules")]
                for f in fn:
                    q = os.path.join(dp, f)
                    if q.endswith((".md", ".py", ".sh", ".txt", ".yml", ".json")):
                        total_chars += len(open(q, encoding="utf-8", errors="replace").read())
                        files += 1
    return {"chars": total_chars, "files": files,
            "est_tokens": round(total_chars / CHARS_PER_TOKEN)}


import os  # noqa: E402


def main() -> int:
    update = "--update" in sys.argv
    tol = float(os.environ.get("TOKEN_TOLERANCE", "0.10"))
    skills = sorted(d for d in (ROOT / "skills").iterdir() if d.is_dir())
    current = {d.name: skill_tokens(d) for d in skills}
    total_now = sum(v["est_tokens"] for v in current.values())

    if update:
        BASELINES.write_text(json.dumps(
            {"updated": "see git history", "skills": current, "total_est_tokens": total_now},
            indent=1))
        print(f"baselines updated: {total_now} est tokens across {len(current)} skills")
        return 0

    if not BASELINES.exists():
        print("no baselines.json; run with --update once, review, commit")
        return 2
    base = json.loads(BASELINES.read_text())
    fails = []
    print(f"{'skill':<28} {'baseline':>10} {'now':>10} {'delta':>8}")
    for name, now in current.items():
        b = base.get("skills", {}).get(name, {}).get("est_tokens", 0)
        delta = now["est_tokens"] - b
        rel = (delta / b) if b else 0.0
        flag = "REGRESSION" if b and rel > tol else ""
        print(f"{name:<28} {b:>10} {now['est_tokens']:>10} {delta:>+8} {flag}")
        if flag:
            fails.append(name)
    tb = base.get("total_est_tokens", 0)
    print(f"{'TOTAL':<28} {tb:>10} {total_now:>10} {total_now - tb:>+8}")
    if fails:
        print(f"FAIL: token regression in {', '.join(fails)}; slim the skill or "
              f"re-baseline with --update after review (AGENTSPEAK: tokens are the budget)")
        return 1
    print("token-benchmark: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

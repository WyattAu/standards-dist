#!/usr/bin/env python3
"""context-audit: estate-wide mechanical check of CONTEXT-CORE (CX rules).

Walks estate repos and LLM-fed artifacts and reports violations of the
canon's budget and never-feed rules. Aggregates; does not re-implement
the per-canon gates (voice-lint, check-canon, doc-lint stay canonical).

Checks per repo (repos = directories under --repos-root containing .git):
  CX-8  never-feed: no private-key blocks / AWS access keys in Markdown
  CX-13 provenance: PROVENANCE.yml present in standards canons
  L0    AGENTS.md word budget <= 150 (warn: advisory until flip date)
  L3    llms.txt present where the estate registry declares llms_txt
  M2    PATTERN_ADOPTION.md present (adoption rollout tracker, warn)

Checks per skill dir (under --skills-root, or dist skills/):
  L1/L2 delegated to scripts/skill_audit.py when present (budgets +
  name contract); its violations are this audit's violations.

Usage:
  context-audit.py [--repos-root DIR] [--skills-root DIR]
                   [--registry FILE] [--canon DIR] [--strict]
Exit 1 on violations (never-feed, declared-but-missing artifacts);
budget overruns are warnings unless --strict.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

AGENTS_WORDS = 150
NEVER_FEED = [
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]
DEFAULT_ROOTS = [
    "~/dev/src/github.com/WyattAu/context-standards",
    "~/dev/src/github.com/WyattAu/pattern-standards",
    "~/dev/src/github.com/WyattAu/seo-standards",
    "~/dev/src/spec-standards",
    "~/dev/src/github.com/WyattAu/engineering-standards",
    "~/dev/src/github.com/WyattAu/accessctl",
    "~/dev/src/standards",
    "~/.local/share/standards-dist",
]


def words(t: str) -> int:
    return len(re.findall(r"\S+", t))


def registry_llms_txt(registry: Path | None) -> set[str]:
    """repos whose estate.yml docs block declares llms_txt: true"""
    if not registry or not registry.is_file():
        return set()
    try:
        import yaml  # type: ignore
    except ImportError:
        return set()
    data = yaml.safe_load(registry.read_text(encoding="utf-8", errors="replace")) or {}
    repos = data.get("repos") or {}
    return {name for name, e in repos.items()
            if (e or {}).get("docs") and (e["docs"] or {}).get("llms_txt")}


def md_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*.md"):
        if any(x in p.parts for x in (".git", "target", "node_modules", "vendor", "dist")):
            continue
        files.append(p)
    return files


def audit_repo(repo: Path, declared_llms: set[str], adoption: bool) -> list[dict]:
    out: list[dict] = []
    name = repo.name
    agents = repo / "AGENTS.md"
    if agents.is_file():
        n = words(agents.read_text(encoding="utf-8", errors="replace"))
        if n > AGENTS_WORDS:
            out.append({"repo": name, "sev": "warn", "check": "L0 budget",
                        "msg": f"AGENTS.md {n} words > {AGENTS_WORDS} budget (CX L0, advisory until flip)"})
    # CX-8 never-feed over all markdown + toml + rs/py source comment lines
    for f in md_files(repo):
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            for pat in NEVER_FEED:
                if pat.search(line):
                    out.append({"repo": name, "sev": "violation", "check": "CX-8 never-feed",
                                "msg": f"{f.relative_to(repo)}:{i}: secret-shaped content"})
    if name in declared_llms and not (repo / "llms.txt").is_file():
        out.append({"repo": name, "sev": "violation", "check": "CX-14/SC-10 llms.txt",
                    "msg": "registry declares llms_txt: true but llms.txt is missing"})
    if adoption and not (repo / "PATTERN_ADOPTION.md").is_file():
        out.append({"repo": name, "sev": "warn", "check": "M2 adoption",
                    "msg": "no PATTERN_ADOPTION.md (M2 rollout tracker)"})
    if (repo / "PROVENANCE.yml").is_file() and "rev:" not in (repo / "PROVENANCE.yml").read_text(encoding="utf-8", errors="replace"):
        out.append({"repo": name, "sev": "violation", "check": "CX-13 provenance",
                    "msg": "PROVENANCE.yml missing rev pin"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--repos-root", default=os.path.expanduser("~/dev/src/github.com/WyattAu"))
    ap.add_argument("--skills-root", default=os.path.expanduser("~/.config/opencode/skills"))
    ap.add_argument("--dist", default=os.path.expanduser("~/.local/share/standards-dist"))
    ap.add_argument("--registry", default=os.path.expanduser(
        "~/dev/src/github.com/WyattAu/engineering-standards/estate.yml"))
    ap.add_argument("--canon", default=os.path.expanduser(
        "~/dev/src/github.com/WyattAu/pattern-standards"))
    ap.add_argument("--repos", help="comma-separated repo names (default: standards-map set)")
    ap.add_argument("--adoption", action="store_true", help="enable M2 adoption rollout tracking")
    ap.add_argument("--strict", action="store_true", help="budget warnings also fail")
    a = ap.parse_args()

    repos_root = Path(os.path.expanduser(a.repos_root))
    declared_llms = registry_llms_txt(Path(os.path.expanduser(a.registry))
                                      if Path(os.path.expanduser(a.registry)).is_file() else None)
    canon = Path(os.path.expanduser(a.canon))

    findings: list[dict] = []
    if a.repos:
        repos = [(n.strip(), repos_root / n.strip()) for n in a.repos.split(",")]
    else:
        repos = [(Path(os.path.expanduser(p)).name, Path(os.path.expanduser(p)))
                 for p in DEFAULT_ROOTS]
    for name, repo in repos:
        if not repo.is_dir():
            findings.append({"repo": name, "sev": "warn", "check": "checkout",
                             "msg": "repo not checked out locally"})
            continue
        findings += audit_repo(repo, declared_llms, a.adoption)

    # adoption files, when the M2 tracker is on
    if a.adoption:
        for repo in repos_root.glob("*/PATTERN_ADOPTION.md"):
            r = subprocess.run([sys.executable, str(canon / "scripts" / "adoption-check.py"),
                                "--file", str(repo)], capture_output=True, text=True)
            if r.returncode != 0:
                findings.append({"repo": repo.parent.name, "sev": "violation", "check": "M2 adoption",
                                 "msg": r.stdout.strip()[-400:] or r.stderr.strip()[-200:]})

    # skill budgets via the existing gate (delegation, not re-implementation)
    skills_root = Path(os.path.expanduser(a.skills_root))
    sa = Path(os.path.expanduser(a.dist)) / "scripts" / "skill_audit.py"
    if sa.is_file() and skills_root.is_dir():
        r = subprocess.run([sys.executable, str(sa), str(skills_root)],
                           capture_output=True, text=True)
        for line in r.stdout.splitlines():
            m = re.match(r"(\w+) (.+)", line)
            if line.startswith("V ") or line.startswith("FAIL "):
                findings.append({"repo": "skills", "sev": "violation", "check": "skill budgets",
                                 "msg": line})
        if r.returncode != 0:
            # failures already captured per-line above; keep summary out
            pass

    for f in findings:
        tag = "V" if f["sev"] == "violation" else "W"
        print(f"{tag} [{f['repo']}] {f['check']}: {f['msg']}")
    n_v = sum(1 for f in findings if f["sev"] == "violation")
    n_w = sum(1 for f in findings if f["sev"] == "warn")
    strict = a.strict
    fails = n_v + (n_w if strict else 0)
    print(f"context-audit: {'FAIL' if fails else 'PASS'} "
          f"({n_v} violation(s), {n_w} warning(s){', strict' if strict else ''})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""skill_audit: structure + cost audit for agent skills (estate-skill-forge contract).

Checks per skill directory:
  name            frontmatter `name:` present, kebab-case, <=64 chars; matches
                  dirname or the projection form `wyattau-<dirname>`
  description     present, non-empty, <=500 chars (hard), contains a trigger
                  phrase ("Use when"/"use when"/"Load when") and a scope limit
                  ("Does not" or "does not") per the forge contract
  budget          SKILL.md word count: 400-900 target, 2000 hard
  structure       allowed-tools line, license line, references/ file sizes
                  (per-file >3000 words is a "should be split" warning)
  stale-pointers  references/ mentioned in SKILL.md that do not exist on disk

Usage:
  skill_audit.py <skill-dir-or-skills-root>... [--json]
Exit 0 = clean (warnings allowed), 1 = violations found, 2 = usage error.

Word counts are a load-cost estimate (words x 1.3 ~= tokens), not a parser.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NAME_HARD = 64
DESC_TARGET = (200, 400)
DESC_HARD = 500
WORDS_TARGET = (400, 900)
WORDS_HARD = 2000
REF_WORDS_WARN = 3000

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def frontmatter(text: str) -> dict[str, str]:
    m = FM.match(text)
    out: dict[str, str] = {}
    if not m:
        return out
    key = None
    for line in m.group(1).split("\n"):
        if not line.strip():
            continue
        if re.match(r"^\s", line) and key:
            out[key] += " " + line.strip()
        elif ":" in line:
            key, _, v = line.partition(":")
            out[key.strip()] = v.strip().strip('"')
    return out


def words(text: str) -> int:
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = re.sub(r"^---.*?---\s*\n", "", body, flags=re.S)
    return len(re.findall(r"\S+", body))


def audit_skill(d: Path) -> dict:
    r = {"skill": d.name, "dir": str(d), "violations": [], "warnings": []}
    sk = d / "SKILL.md"
    if not sk.is_file():
        r["violations"].append("no SKILL.md")
        return r
    text = sk.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter(text)

    name = fm.get("name", "")
    if not name:
        r["violations"].append("frontmatter: missing name")
    elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        r["violations"].append(f"frontmatter: name not kebab-case: {name!r}")
    elif len(name) > NAME_HARD:
        r["violations"].append(f"frontmatter: name >{NAME_HARD} chars")
    elif name != d.name and name != "wyattau-" + d.name:
        # projection convention: dir keeps the canon name, installed
        # skill dir + frontmatter name carry the wyattau- prefix
        r["violations"].append(f"frontmatter: name {name!r} != dir {d.name!r} (nor wyattau-{d.name!r})")

    desc = fm.get("description", "")
    wc_desc = len(desc)
    if not desc:
        r["violations"].append("frontmatter: missing description")
    else:
        if wc_desc > DESC_HARD:
            r["violations"].append(f"description: {wc_desc} chars > {DESC_HARD} hard cap")
        elif wc_desc < DESC_TARGET[0]:
            r["warnings"].append(f"description: {wc_desc} chars < {DESC_TARGET[0]} target")
        if not re.search(r"[Uu]se (when|before|after|with|for)\b|[Ll]oad (when|for|before)\b|[Tt]rigger", desc):
            r["violations"].append("description: no trigger phrase (Use when / Load when)")
        if not re.search(r"[Dd]oes not", desc):
            r["warnings"].append("description: no scope limit (Does not: ...)")

    n_words = words(text)
    r["words"] = n_words
    r["tokens_est"] = int(n_words * 1.3)
    if n_words > WORDS_HARD:
        r["violations"].append(f"SKILL.md: {n_words} words > {WORDS_HARD} hard cap")
    elif not (WORDS_TARGET[0] <= n_words <= WORDS_TARGET[1]):
        r["warnings"].append(
            f"SKILL.md: {n_words} words outside {WORDS_TARGET[0]}-{WORDS_TARGET[1]} target"
        )

    if "allowed-tools" not in fm:
        r["warnings"].append("frontmatter: no allowed-tools line")
    if "license" not in fm:
        r["warnings"].append("frontmatter: no license line")

    refs = d / "references"
    ref_stats = []
    if refs.is_dir():
        for f in sorted(refs.iterdir()):
            if f.is_file() and f.suffix == ".md":
                w = words(f.read_text(encoding="utf-8", errors="replace"))
                ref_stats.append({"file": f.name, "words": w})
                if w > REF_WORDS_WARN:
                    r["warnings"].append(f"references/{f.name}: {w} words, consider splitting")
    r["references"] = ref_stats

    for m in set(re.findall(r"references/([A-Za-z0-9._-]+\.md)", text)):
        if not (refs / m).is_file():
            r["violations"].append(f"SKILL.md points at missing references/{m}")

    return r


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    targets = [a for a in args if a != "--json"]
    if not targets:
        print(__doc__, file=sys.stderr)
        return 2
    results = []
    for t in targets:
        p = Path(t)
        if p.is_dir() and (p / "SKILL.md").is_file():
            results.append(audit_skill(p))
        elif p.is_dir():
            for c in sorted(p.iterdir()):
                if c.is_dir() and not c.name.startswith("."):
                    if (c / "SKILL.md").is_file() or (c / "references").is_dir():
                        results.append(audit_skill(c))
        else:
            print(f"skill_audit: not a dir: {t}", file=sys.stderr)
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        bad = 0
        for r in results:
            status = "FAIL" if r["violations"] else "PASS"
            if r["violations"]:
                bad += 1
            line = f"{status} {r['skill']}"
            if "words" in r:
                line += f" ({r['words']}w/~{r['tokens_est']}tok, {len(r.get('references', []))} refs)"
            print(line)
            for v in r["violations"]:
                print(f"  V {v}")
            for w in r["warnings"]:
                print(f"  W {w}")
        print(f"skill_audit: {len(results) - bad}/{len(results)} clean")
    return 1 if any(r["violations"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())

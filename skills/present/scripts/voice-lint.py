#!/usr/bin/env python3
"""voice-lint: prose register gate for the WyattAu estate (PRESENT/AGENTSPEAK).

Fence-aware Markdown scan. Checks:
  em-dash rule (DOC-STYLE 1)          the character appears in no prose
  PR-6/AS filler list                 tokens that subtract information
  PR-8/AS-4 hedge list                hedges replaced by explicit state
  AS-7 decoration                     emoji in headings/body of estate docs

Usage:
  voice-lint.py <files-or-dirs>...            advisory: report, exit 0
  voice-lint.py --strict <files-or-dirs>...   blocking: exit 1 on findings

Code fences are stripped before scanning. Findings print file:line.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

EM = "\u2014"
FILLERS = [
    r"it is worth noting", r"it's worth noting", r"please note that",
    r"in order to", r"at the end of the day", r"needless to say",
    r"\bbasically\b", r"\bessentially\b", r"\butilize\b", r"\butilizing\b",
    r"\bleverage\b(?=.*\bthe\b)", r"\bin terms of\b",
]
HEDGES = [
    r"\bI think\b", r"\bI believe\b", r"\bperhaps\b", r"\bmaybe we (should|could)\b",
    r"\bmight be worth\b", r"\bit seems\b", r"\barguably\b", r"\bsome might say\b",
]
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\u2705\u274c\u26a0\ufe0f]", flags=re.UNICODE
)

CHECKS = [("filler (PRESENT PR-6)", [re.compile(p, re.I) for p in FILLERS]),
          ("hedge (AGENTSPEAK AS-4)", [re.compile(p, re.I) for p in HEDGES]),
          ("em-dash (DOC-STYLE 1)", [re.compile(EM)]),
          ("decoration (AGENTSPEAK AS-7)", [EMOJI])]


def strip_fences(text: str) -> str:
    # Fences removed entirely; code spans removed because a mention inside
    # backticks is a definition of a banned pattern, not a use of it
    # (the DOC-STYLE printf-escape precedent, generalised).
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "``", text)


def md_files(targets: list[str]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        p = Path(t)
        if p.is_file() and p.suffix == ".md":
            out.append(p)
        elif p.is_dir():
            for dp, dn, fn in os.walk(p):
                dn[:] = [x for x in dn if x not in (".git", "node_modules", "vendor", "dist")]
                out += [Path(os.path.join(dp, f)) for f in fn if f.endswith(".md")]
    return out


def main() -> int:
    args = sys.argv[1:]
    strict = "--strict" in args
    targets = [a for a in args if a != "--strict"]
    if not targets:
        print("usage: voice-lint.py [--strict] <files-or-dirs>...", file=sys.stderr)
        return 2
    findings = 0
    for p in md_files(targets):
        body = strip_fences(p.read_text(encoding="utf-8", errors="replace"))
        for lineno, line in enumerate(body.split("\n"), 1):
            for label, patterns in CHECKS:
                for pat in patterns:
                    if pat.search(line):
                        findings += 1
                        print(f"{p}:{lineno}: {label}: {line.strip()[:90]}")
    verdict = "FAIL" if (strict and findings) else "PASS"
    print(f"voice-lint: {verdict} ({findings} finding(s){', strict' if strict else ', advisory'})")
    return 1 if (strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())

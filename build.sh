#!/usr/bin/env bash
# Rebuild the projections from the canon repos and verify freshness (SC-11).
# Usage: build.sh            rebuild references/scripts + PROVENANCE from canon checkouts
#        build.sh --check    verify pinned revs are current on origin/main (exit 1 = stale)
set -euo pipefail
cd "$(dirname "$0")"
SPEC_CANON="${SPEC_CANON:-$HOME/dev/src/spec-standards}"
ENG_CANON="${ENG_CANON:-/tmp/opencode/rollout/eng}"
PATTERN_CANON="${PATTERN_CANON:-$HOME/dev/src/github.com/WyattAu/pattern-standards}"
CONTEXT_CANON="${CONTEXT_CANON:-$HOME/dev/src/github.com/WyattAu/context-standards}"

pin() { git -C "$1" rev-parse --short HEAD; }

if [ "${1:-}" = "--diff" ]; then
  # machine-readable drift: what changed between each skill's pinned rev and
  # the canon head (the diff the MCP drift research says registries lack).
  out="["; first=1
  for skill in skills/*/; do
    prov="$skill/PROVENANCE.yml"
    [ -f "$prov" ] || continue
    pinned=$(awk '/^rev:/{print $2}' "$prov")
    src_repo=$(awk '/^source:/{print $2}' "$prov")
    tmp=$(mktemp -d)
    git clone --quiet --filter=blob:none "https://github.com/${src_repo}.git" "$tmp" 2>/dev/null || { echo "[]"; exit 0; }
    head=$(git -C "$tmp" rev-parse --short HEAD)
    if [ "$pinned" != "$head" ]; then
      files=$(git -C "$tmp" diff --name-only "$pinned" "$head" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().split()))')
      [ $first -eq 0 ] && out="$out,"
      first=0
      out="$out{"skill":"${skill#skills/}","pinned":"$pinned","head":"$head","changed_files":$files}"
    fi
    rm -rf "$tmp"
  done
  echo "$out]"
  exit 0
fi

if [ "${1:-}" = "--check" ]; then
  stale=0
  for skill in skills/*/; do
    pinned=$(awk '/^rev:/{print $2}' "$skill/PROVENANCE.yml")
    src_repo=$(awk '/^source:/{print $2}' "$skill/PROVENANCE.yml")
    origin=$(git ls-remote "https://github.com/${src_repo}.git" refs/heads/main 2>/dev/null | cut -c1-7)
    if [ -n "$origin" ] && [ "$pinned" != "$origin" ]; then
      echo "STALE: $skill pins $pinned, canon $src_repo is at $origin"; stale=1
    fi
  done
  exit $stale
fi

SREV=$(pin "$SPEC_CANON"); EREV=$(pin "$ENG_CANON")
cp "$SPEC_CANON/SPEC-CORE.md" "$SPEC_CANON/DOC-STYLE.md" skills/spec-standards/references/
cp "$SPEC_CANON/scripts/doc-lint.sh" "$SPEC_CANON/scripts/spec-audit.py" skills/spec-standards/scripts/
cp "$ENG_CANON/OMNI-CORE.md" "$ENG_CANON/DOC-STYLE.md" skills/engineering-standards/references/
STANDARDS_CANON="${STANDARDS_CANON:-$HOME/dev/src/standards}"
STDREV=$(pin "$STANDARDS_CANON")
cp "$STANDARDS_CANON/standards/PRESENT.md" skills/present/references/
cp "$STANDARDS_CANON/standards/AGENTSPEAK.md" skills/agentspeak/references/
for f in present agentspeak; do
  sed -i "s/^rev: .*/rev: $STDREV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/$f/PROVENANCE.yml
done
sed -i "s/^rev: .*/rev: $SREV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/spec-standards/PROVENANCE.yml
sed -i "s/^rev: .*/rev: $EREV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/engineering-standards/PROVENANCE.yml
PREV=$(pin "$PATTERN_CANON")
mkdir -p skills/pattern-standards/references
cp "$PATTERN_CANON/PATTERN-CORE.md" skills/pattern-standards/references/
cp "$PATTERN_CANON"/references/*.md skills/pattern-standards/references/
mkdir -p skills/pattern-standards/scripts
cp "$PATTERN_CANON/scripts/route.py" skills/pattern-standards/scripts/route.py
CONTEXT_REV=$(pin "$CONTEXT_CANON")
mkdir -p skills/context-standards/references
cp "$CONTEXT_CANON/CONTEXT-CORE.md" skills/context-standards/references/
cp "$CONTEXT_CANON"/references/*.md skills/context-standards/references/
mkdir -p skills/context-standards/scripts
cp "$CONTEXT_CANON/scripts/context-audit.py" skills/context-standards/scripts/
sed -i "s/^rev: .*/rev: $CONTEXT_REV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/context-standards/PROVENANCE.yml
sed -i "s/^rev: .*/rev: $PREV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/pattern-standards/PROVENANCE.yml
VLREV=$(pin "$STANDARDS_CANON")
cp "$STANDARDS_CANON/scripts/voice-lint.py" scripts/voice-lint.py
mkdir -p skills/present/scripts
cp "$STANDARDS_CANON/scripts/voice-lint.py" skills/present/scripts/voice-lint.py
sed -i "s/^rev: .*/rev: $VLREV/; s/^rebuilt: .*/rebuilt: \"$(date -u +%Y-%m-%dT%H:%M:%SZ) by build.sh\"/" skills/present/PROVENANCE.yml
echo "rebuilt projections (spec=$SREV eng=$EREV standards=$STDREV patterns=$PREV context=$CONTEXT_REV voice-lint=$VLREV)"

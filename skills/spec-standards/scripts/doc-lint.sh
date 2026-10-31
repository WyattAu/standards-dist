#!/usr/bin/env bash
# doc-lint: tier-aware prose and structure gate (SPEC-CORE §9).
# Usage: scripts/doc-lint.sh [s|k|a|d] [--req-check]
# Runs from the repository root. Scripts are canonical; CI mirrors this
# script exactly (SPEC-CORE SC-9). Exits 1 on any FAIL, 0 otherwise.
set -u

TIER="k"
REQ_CHECK=0
for arg in "$@"; do
  case "$arg" in
    s|k|a|d) TIER="$arg" ;;
    --req-check) REQ_CHECK=1 ;;
    *) echo "usage: doc-lint.sh [s|k|a|d] [--req-check]" >&2; exit 2 ;;
  esac
done

FAILS=0
fail()    { echo "FAIL: $*"; FAILS=$((FAILS + 1)); }
advisory(){ echo "ADVISORY: $*"; }
skip()    { echo "SKIP: $*"; }

EM=$(printf '\342\200\224')   # the em-dash character, constructed not typed

# Repo-level scope excludes (.doclint-exclude, one directory name per
# line): product content and vendored trees are not estate docs. Entries
# are matched as directory basenames by grep/find.
EXTRA_EXCLUDES=""
if [ -f .doclint-exclude ]; then
  while IFS= read -r entry; do
    entry=$(echo "$entry" | tr -d '[:space:]')
    [ -n "$entry" ] && case "$entry" in \#*) ;; *) EXTRA_EXCLUDES="$EXTRA_EXCLUDES --exclude-dir=$entry";; esac
  done < .doclint-exclude
fi

# Dated advisory windows (README matrix): gates escalate to blocking
# automatically on their date. No manual flip, nothing to forget.
TODAY=$(date +%Y%m%d)
WINDOW_2027_04=20270401   # markdownlint / llms.txt / truth-table at k,d
WINDOW_2027_01=20270101   # REQ cross-check at s; llms freshness at s,k
SEV_KD="advisory"; [ "$TODAY" -ge "$WINDOW_2027_04" ] && SEV_KD="fail"
SEV_0101="advisory"; [ "$TODAY" -ge "$WINDOW_2027_01" ] && SEV_0101="fail"

# --- 1. Character rule (DOC-STYLE §1): no em-dash in any Markdown -------
HITS=$(grep -rIn --include='*.md' "$EM" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist $EXTRA_EXCLUDES 2>/dev/null || true)
if [ -n "$HITS" ]; then
  fail "em-dash present (DOC-STYLE §1); first offenders:"
  echo "$HITS" | head -5
fi

# --- 2. Status stamps (SPEC-CORE §5): FROZEN needs a date,
#        SUPERSEDED needs a successor -------------------------------------
STAMP_LINES=$(grep -rhE 'Status:.*(FROZEN|SUPERSEDED)' --include='*.md' . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=dist $EXTRA_EXCLUDES 2>/dev/null || true)
while IFS= read -r LINE; do
  [ -z "$LINE" ] && continue
  case "$LINE" in
    *FROZEN*)
      echo "$LINE" | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}' \
        || fail "FROZEN stamp without ISO date (SPEC-CORE §5): $LINE"
      ;;
    *SUPERSEDED*)
      echo "$LINE" | grep -q ' by ' \
        || fail "SUPERSEDED stamp without successor (SPEC-CORE §5): $LINE"
      ;;
  esac
done <<EOF2
$STAMP_LINES
EOF2

# --- 3. Truth table (SPEC-CORE §3): heading present, paths exist --------
# Blocking at tiers s,a; advisory at tier k until 2027-04 (README matrix).
truth_check() {  # $1 = severity: fail | advisory | skip
  local SEV="$1" CONTRACT SECTION ROWS PATHS P
  if [ -f AGENTS.md ]; then CONTRACT=AGENTS.md; else CONTRACT=README.md; fi
  if [ ! -f "$CONTRACT" ]; then
    "$SEV" "no contract file (AGENTS.md or README.md) for the truth table (SC-1)"
    return
  fi
  SECTION=$(awk '/^## Where the truth lives/{f=1;next} /^## /{f=0} f' "$CONTRACT")
  ROWS=$(printf '%s\n' "$SECTION" | grep -cE '^\|.*\|[[:space:]]*`[^`]+`[[:space:]]*\|[[:space:]]*$' || true)
  if [ "${ROWS:-0}" -lt 1 ]; then
    "$SEV" "$CONTRACT: truth table has no path rows (SPEC-CORE §3)"
    return
  fi
  PATHS=$(printf '%s\n' "$SECTION" | grep -oE '`[^`]+`' | sed 's/`//g' | sort -u)
  while IFS= read -r P; do
    [ -z "$P" ] && continue
    if [ ! -e "$P" ]; then "$SEV" "truth-table path missing: $P (SC-1)"; fi
  done <<EOF3
$PATHS
EOF3
}
case "$TIER" in
  s|a) truth_check fail ;;
  k)   truth_check "$SEV_KD" ;;
  d)   skip "truth table not required at tier d" ;;
esac

# --- 4. llms.txt projection (SPEC-CORE SC-10) ---------------------------
# Blocking at tiers s,a; advisory at tiers k,d until 2027-04.
llms_check() {  # $1 = severity
  local SEV="$1"
  if [ ! -f llms.txt ]; then "$SEV" "llms.txt missing (SC-10)"; return; fi
  if grep -nE 'TODO|PLACEHOLDER|TBD|FIXME' llms.txt >/dev/null 2>&1; then
    "$SEV" "llms.txt contains placeholders (SC-10):"
    grep -nE 'TODO|PLACEHOLDER|TBD|FIXME' llms.txt | head -5
  fi
}
case "$TIER" in
  s|a) llms_check fail ;;
  k|d) llms_check "$SEV_KD" ;;
esac

# --- 5. Oracle line (SPEC-CORE §6), tier S ------------------------------
if [ "$TIER" = "s" ]; then
  while IFS= read -r F; do
    [ -z "$F" ] && continue
    if ! grep -q 'Oracle:' "$F" && ! grep -q 'No-oracle' "$F"; then
      fail "$F: no 'Oracle:' or 'No-oracle:' line (SPEC-CORE §6)"
    fi
  done <<EOF5
$(find . -name 'SPEC*.md' -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/dist/*' $EXTRA_FIND 2>/dev/null)
EOF5
fi

# --- 6. REQ cross-check (SPEC-CORE §4): advisory ------------------------
if [ "$TIER" = "s" ] || [ "$REQ_CHECK" -eq 1 ]; then
  SPECS=$(find . -name 'SPEC*.md' -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/dist/*' $EXTRA_FIND 2>/dev/null || true)
  SPEC_REQS=$(grep -rhoE 'REQ-[A-Z][A-Z0-9]*-[0-9]{3}' $SPECS 2>/dev/null | sort -u || true)
  CODE_REQS=$(grep -rhoE 'REQ-[A-Z][A-Z0-9]*-[0-9]{3}' \
    --include='*.py' --include='*.rs' --include='*.sh' --include='*.hs' \
    --include='*.lean' --include='*.ts' --include='*.go' --include='*.c' \
    --include='*.h' --include='*.cpp' --include='*.dart' \
    . --exclude-dir=.git 2>/dev/null | sort -u || true)
  ORPHANS=$(comm -23 <(printf '%s\n' "$SPEC_REQS" | sort -u) <(printf '%s\n' "$CODE_REQS" | sort -u) | sed '/^$/d' || true)
  if [ -n "$ORPHANS" ]; then
    if [ "$SEV_0101" = "fail" ]; then
      fail "REQs defined in specs with no code tag (SPEC-CORE §4): $(echo "$ORPHANS" | tr '\n' ' ')"
    else
      advisory "REQs defined in specs with no code tag (SPEC-CORE §4): $(echo "$ORPHANS" | tr '\n' ' ')"
    fi
  fi
else
  skip "REQ cross-check not enabled (tier $TIER, no --req-check)"
fi

# --- 7. markdownlint (optional tool; used when installed) ---------------
# Blocking at tier s; elsewhere advisory until 2027-04 (SEV_KD above).
# A lint TIMEOUT (124) is environmental: the tool could not run, so the
# gate SKIPs locally and CI (which mirrors this script with reliable
# egress) decides. Real findings from a running linter still fail.
md_fail() {
  if [ "$TIER" = "s" ] || [ "$SEV_KD" = "fail" ]; then fail "$*"; else advisory "$*"; fi
}
run_lint() {  # $1 = command...; findings on stdout+stderr, rc: 0 clean, 124 timeout, other = findings
  timeout "${MD_TIMEOUT:-120}" "$@" 2>&1
}
EXTRA_FIND=""  # find-based SPEC discovery keeps built-in prunes only
lint_one() {  # $@ = linter argv
  OUT=$(run_lint "$@"); rc=$?
  if [ $rc -eq 124 ]; then
    skip "markdownlint timed out locally (network/tool); CI decides"
  elif [ $rc -ne 0 ]; then
    md_fail "markdownlint reported issues:" && printf '%s\n' "$OUT" | head -5
  fi
}
if command -v markdownlint >/dev/null 2>&1; then
  if [ -f .markdownlint.json ]; then lint_one markdownlint "**/*.md" --config .markdownlint.json
  else lint_one markdownlint "**/*.md"; fi
elif command -v npx >/dev/null 2>&1; then
  if [ -f .markdownlint.json ]; then lint_one npx -y markdownlint-cli "**/*.md" --config .markdownlint.json
  else lint_one npx -y markdownlint-cli "**/*.md"; fi
else
  skip "markdownlint not installed (nix devShell provides it; see flake.nix)"
fi

if [ "$FAILS" -gt 0 ]; then
  echo "doc-lint: FAIL (tier $TIER, $FAILS failure(s))"
  exit 1
fi
echo "doc-lint: PASS (tier $TIER)"

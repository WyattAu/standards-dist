# DOC-STYLE: documentation rules for every repository in the estate

Canonical home: `spec-standards` (moved from engineering-standards,
see spec-standards `docs/adr/0003-docstyle-move.md`). These rules apply to
every Markdown document in every WyattAu repository: READMEs, AGENTS.md
files, design documents, runbooks, and ledgers. Normative identifiers used
below cite `SPEC-CORE §N`.

## 1. Character rule: no em-dash

The em-dash character does not appear in any document. Use a colon, a
comma, a semicolon, or parentheses instead. The character carries no
meaning that those do not, and it renders inconsistently across terminals
and fonts. This file itself is written without one; the check below
constructs the character with `printf` so the rule is self-consistent.

Scope: the rule covers estate-authored documents. Vendored trees
(`node_modules/`, `vendor/`, `dist/`) are upstream's prose and are
excluded from the gate's scan (enforced in `doc-lint.sh` since 0.2.1;
motivated by a committed vendored tree failing the gate on first wire).

Check any tree with:

```bash
grep -rn --include='*.md' "$(printf '\342\200\224')" .
```

The count must be zero. Wire the check into the repository's lint workflow
where a docs tree exists; `scripts/doc-lint.sh` in this repository is the
canonical implementation (SPEC-CORE §9).

## 2. Register rule: technical, concise, non-handwavy

Every sentence in a document does exactly one of the following:

1. States a fact and cites where it is enforced or defined (file path,
   theorem name, test name, commit, or external link).
2. Gives a procedure (commands, in execution order, with expected output).
3. States a decision and its reason, with the rejected alternatives
   named.

Marketing adjectives do not appear in documentation. Performance claims
carry measured numbers and the measurement method. "Fast" is not a claim;
"P99 under 5 ms at 10k req/s, measured by criterion commit `abc1234`" is.

## 3. Citation rule: unlinked claims are draft material

A claim that cannot cite its enforcement point or source is not
documentation; it is a TODO. The citation forms accepted in this estate:

- Repository link: `[name](https://github.com/WyattAu/name)`.
- File path: `src/service/sending/sender.rs`.
- Theorem or test name: `take_conserves`, `fresh_chain_converges_with_boot_patches`.
- External source: author, title, year, link.
- Commit: short hash plus one-line subject.

Spec-level extension (SPEC-CORE SC-3): a normative statement in a spec
cites its enforcement point (theorem, golden-vector set, gate, or test);
external normative sources additionally satisfy SC-8 (vendored under
`docs/refs/` or stably linked).

## 4. Sweep procedure for existing documents

```bash
grep -rl --include='*.md' "$(printf '\342\200\224')" . | while read -r f; do
  sed -i "$(printf 's/\xe2\x80\x94//g')" "$f"
done
```

This mechanical sweep deletes the character; it cannot choose a
replacement. Review the diff before committing: the surrounding sentence
must still read correctly with the punctuation removed, and most sentences
need a colon or comma inserted by hand.

## 5. Status stamps and freeze discipline

Normative documents carry a lifecycle status line per SPEC-CORE §5
(`DRAFT`, `REVIEW`, `CURRENT`, `FROZEN (date)`, `SUPERSEDED by <path>`).
A frozen document is append-only; a superseded document keeps its original
text visible and points at its successor. `doc-lint.sh` fails on a
`FROZEN` stamp without a date and on a `SUPERSEDED` stamp without a
successor pointer.

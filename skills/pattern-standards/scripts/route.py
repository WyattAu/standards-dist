#!/usr/bin/env python3
"""route: deterministic traversal of the pattern decision graph.

Parses references/decision-graph.md (### NXX headings with K:/M:/A:/R:
lines) and emits a node block, so agents traverse the graph at one
script-call cost instead of reading the file.

Usage:
  route.py --task "paginated admin table over a multi-tenant audit log"
  route.py --node N08
  route.py --list

--task scores the task's words against each node's K (keyword) line and
prints the best node's M/A/R block. Exit 0 on a confident match; exit 1
with candidate nodes when the score is 0 or tied (the caller should then
ask the user or read decision-graph.md directly). Exit 2 on usage or
missing graph.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_GRAPH = Path(__file__).resolve().parent.parent / "references" / "decision-graph.md"


def parse_graph(path: Path) -> dict[str, dict[str, str]]:
    nodes: dict[str, dict[str, str]] = {}
    cur: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### (N\d+) · (.+)$", line)
        if m:
            cur = m.group(1)
            nodes[cur] = {"name": m.group(2).strip(), "M": "", "A": "", "R": "", "K": ""}
            continue
        if cur:
            for k in ("K", "M", "A", "R"):
                if line.startswith(f"{k}: "):
                    nodes[cur][k] = line[len(k) + 2:].strip()
    return nodes


def score(nodes: dict[str, dict[str, str]], task: str) -> list[tuple[int, str]]:
    words = set(re.findall(r"[a-z0-9]+", task.lower()))
    scored = []
    for nid, n in nodes.items():
        kws = set(re.findall(r"[a-z0-9]+", n["K"].lower()))
        hits = 0
        for w in words:
            for k in kws:
                if w == k or (len(w) >= 4 and len(k) >= 4 and (w.startswith(k) or k.startswith(w))):
                    hits += 1
                    break
        scored.append((hits, nid))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def emit(nodes: dict[str, dict[str, str]], nid: str) -> None:
    n = nodes[nid]
    print(f"{nid} · {n['name']}")
    print(f"M (mandatory): {n['M']}")
    print(f"A (ask, in order): {n['A']}")
    print(f"R (refuse): {n['R']}")
    print("Union rule: tasks spanning several nodes union their M sets and walk all A chains.")


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--task")
    ap.add_argument("--node")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--eval", nargs="?", const="scripts/route-eval.json", default=None)
    ap.add_argument("--adopt", metavar="NODE", help="draft PATTERN_ADOPTION.md rows for a node's M set")
    ap.add_argument("--repo", help="repo root for --adopt (default: cwd)")
    ap.add_argument("--graph", default=str(DEFAULT_GRAPH))
    args = ap.parse_args()
    graph = Path(args.graph)
    if not graph.is_file():
        print(f"route: graph not found: {graph}", file=sys.stderr)
        return 2
    nodes = parse_graph(graph)
    if not nodes:
        print("route: graph parsed empty; format drift?", file=sys.stderr)
        return 2
    if args.list:
        for nid in sorted(nodes):
            print(f"{nid}  {nodes[nid]['name']}")
        return 0
    if args.node:
        if args.node not in nodes:
            print(f"route: unknown node {args.node}", file=sys.stderr)
            return 2
        emit(nodes, args.node)
        return 0
    if args.eval:
        import json
        ev = Path(args.eval)
        if not ev.is_file():
            print(f"route: eval file not found: {ev}", file=sys.stderr)
            return 2
        cases = json.loads(ev.read_text())
        fails = 0
        for c in cases:
            task, expect = c["task"], set(c["expect"])
            scored = score(nodes, task)
            top = scored[0]
            tied = {nid for s, nid in scored if s == top[0]}
            emitted = tied if top[0] > 0 else set()
            ok = expect <= emitted
            if not ok:
                fails += 1
                print(f"FAIL {task!r}: expect {sorted(expect)}, emitted {sorted(emitted)} (top {top[1]} score {top[0]})")
        print(f"route-eval: {len(cases) - fails}/{len(cases)} pass")
        return 1 if fails else 0
    if args.adopt:
        if args.adopt not in nodes:
            print(f"route: unknown node {args.adopt}", file=sys.stderr)
            return 2
        repo = Path(args.repo) if args.repo else Path.cwd()
        n = nodes[args.adopt]
        target = repo / "PATTERN_ADOPTION.md"
        existing = target.read_text(encoding="utf-8") if target.is_file() else ""
        pids = sorted(set(re.findall(r"[TPX]\d+", n["M"])))
        new_rows = []
        for pid in pids:
            if f"| {pid} |" not in existing:
                new_rows.append(f"| {pid} | planned | todo (route.py --adopt {args.adopt} draft; verify against code before promoting) |")
        if not new_rows:
            print(f"route: all M-set patterns for {args.adopt} already declared in {target}")
            return 0
        if not existing:
            header = (f"# PATTERN_ADOPTION: {repo.name}\n\n"
                      "Relationship to the WyattAu pattern canon "
                      "(`github.com/WyattAu/pattern-standards`), validated by "
                      "`scripts/adoption-check.py` per `references/adoption-format.md`. "
                      f"Drafted by `route.py --adopt {args.adopt}`; verify each row "
                      "against the code before promoting.\n\n"
                      "| Pattern | Status | Evidence |\n|---|---|---|\n")
        else:
            header = ""
        target.write_text(header + "\n".join(new_rows) + "\n", encoding="utf-8")
        print(f"route: drafted {len(new_rows)} row(s) into {target} for node {args.adopt}")
        print("verify each row against the code, then promote statuses and fill evidence")
        return 0
    if args.task:
        scored = score(nodes, args.task)
        top, runner_up = scored[0], scored[1] if len(scored) > 1 else (0, "")
        if top[0] == 0:
            print(f"route: no keyword match for {args.task!r}; candidates:")
            for s, nid in scored[:5]:
                print(f"  {nid}  {nodes[nid]['name']}")
            return 1
        if top[0] == runner_up[0]:
            print(f"route: ambiguous between nodes (score {top[0]}); candidates:")
            for s, nid in scored:
                if s == top[0]:
                    print(f"  {nid}  {nodes[nid]['name']}")
            print("Union rule applies: take both M sets, walk both A chains (decision-graph.md §algorithm).")
            return 1
        emit(nodes, top[1])
        return 0
    ap.print_help(file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

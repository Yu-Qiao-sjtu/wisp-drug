#!/usr/bin/env python3
"""wisp-drug skill contract validator (v0.1).

Implements the checks defined in docs/skill-format.md (V1-V10).
Stdlib only. Exit code 0 = pass (warnings allowed), 1 = contract violation.

Usage:
    python tools/validate_skills.py [--root PATH] [--max-entry-lines N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_ENTRY_LINES_DEFAULT = 300
VALID_RUNTIMES = {"uv", "ssh"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------- frontmatter

def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (parsed-frontmatter-subset, body). Minimal YAML subset parser."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    # find closing ---
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, text
    fm_lines = lines[1:close]
    body = "\n".join(lines[close + 1:])
    meta: dict = {}
    current_list: str | None = None
    for raw in fm_lines:
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_list:
            item = line.strip().lstrip("-").strip()
            if item:
                meta.setdefault(current_list, []).append(item)
            continue
        current_list = None
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            # either empty scalar or a list header — decide on next lines
            meta[key] = ""
            current_list = key
            meta[key] = []
        else:
            meta[key] = val.strip("\"'")
    return meta, body


# ------------------------------------------------------------------- checks

def check_skill_dir(skill_dir: Path, rep: Report, max_lines: int) -> dict:
    """Validate one skill directory; return its frontmatter (for graph pass)."""
    name = skill_dir.name
    entry = skill_dir / "SKILL.md"

    # V1
    if not entry.is_file():
        rep.error(f"[V1] {name}: SKILL.md missing")
        return {}

    text = entry.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)

    # V2
    if not meta:
        rep.error(f"[V2] {name}: frontmatter unparseable (--- blocks)")
        return meta
    if meta.get("name") != name:
        rep.error(f"[V2] {name}: frontmatter name={meta.get('name')!r} != dir name {name!r}")
    for field in ("description", "license"):
        if not meta.get(field):
            rep.error(f"[V2] {name}: required field '{field}' missing/empty")

    # V5
    n_lines = len(text.splitlines())
    if n_lines > max_lines:
        rep.error(f"[V5] {name}: SKILL.md has {n_lines} lines (> {max_lines}); split into references/")

    # V6/V7 references index
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        ref_files = sorted(p.name for p in refs_dir.glob("*.md"))
        listed = set(re.findall(r"references/([A-Za-z0-9._-]+\.md)", text))
        for f in ref_files:
            if f not in listed:
                rep.warn(f"[V7] {name}: references/{f} exists but is not indexed in SKILL.md")
        for f in sorted(listed):
            if f not in ref_files:
                rep.error(f"[V6] {name}: SKILL.md indexes references/{f} which does not exist")

    # V8/V9 samples
    has_scripts = (skill_dir / "scripts").is_dir() and any((skill_dir / "scripts").iterdir())
    sample = skill_dir / "samples" / "input.json"
    if has_scripts:
        if not sample.is_file():
            rep.error(f"[V8] {name}: has scripts/ but samples/input.json missing")
        else:
            try:
                data = json.loads(sample.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("requires_network") is True:
                    rep.info(f"[V9] {name}: input.json marks requires_network=true, smoke skipped")
            except json.JSONDecodeError as e:
                rep.error(f"[V8] {name}: samples/input.json is not valid JSON ({e})")

    # V10 env
    env = meta.get("env")
    if isinstance(env, str) and env:  # parsed as scalar if written inline
        env = {"runtime": env}
    if env not in (None, "", []):
        if not isinstance(env, dict):
            rep.error(f"[V10] {name}: env must be a mapping, got {env!r}")
        else:
            runtime = str(env.get("runtime", ""))
            if runtime not in VALID_RUNTIMES:
                rep.error(f"[V10] {name}: env.runtime={runtime!r} not in {sorted(VALID_RUNTIMES)}")
            if runtime == "ssh" and not env.get("capability"):
                rep.error(f"[V10] {name}: env.runtime=ssh requires 'capability'")

    return meta


def check_dependency_graph(metas: dict[str, dict], rep: Report) -> None:
    """V3/V4: existence + DFS cycle/self-loop detection over dependsOn."""
    graph: dict[str, list[str]] = {}
    for name, meta in metas.items():
        deps = meta.get("dependsOn")
        deps = deps if isinstance(deps, list) else ([] if not deps else [deps])
        for dep in deps:
            if dep == name:
                rep.error(f"[V4] {name}: self-dependency in dependsOn")
        graph[name] = [d for d in deps if d != name]

    for name, deps in graph.items():
        for dep in deps:
            if dep not in metas:
                rep.error(f"[V3] {name}: dependsOn references missing skill '{dep}'")

    # DFS cycle detection (iterative, colored)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    for start in graph:
        if color[start] != WHITE:
            continue
        stack = [(start, iter(graph[start]))]
        color[start] = GRAY
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if nxt not in graph:
                    continue
                if color[nxt] == GRAY:
                    rep.error(f"[V4] dependency cycle detected: {node} -> {nxt} (chain includes {start})")
                    continue
                if color[nxt] == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, iter(graph[nxt])))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="wisp-drug skill contract validator")
    ap.add_argument("--root", default=".", help="repo root (contains skills/)")
    ap.add_argument("--max-entry-lines", type=int, default=MAX_ENTRY_LINES_DEFAULT)
    ap.add_argument("--future", action="store_true",
                    help="reserve: also validate future tiers (docker) — currently a no-op")
    args = ap.parse_args()

    root = Path(args.root)
    skills_root = root / "skills"
    rep = Report()

    if not skills_root.is_dir():
        rep.warn(f"no skills/ directory under {root} — nothing to validate yet")
    else:
        metas = {}
        for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            meta = check_skill_dir(skill_dir, rep, args.max_entry_lines)
            if meta:
                metas[skill_dir.name] = meta
        check_dependency_graph(metas, rep)

    for w in rep.warnings:
        print(f"WARN  {w}")
    for i in rep.infos:
        print(f"INFO  {i}")
    for e in rep.errors:
        print(f"ERROR {e}")

    n_skills = len(list(skills_root.glob("*/SKILL.md"))) if skills_root.is_dir() else 0
    print(f"\n{'PASS' if rep.ok else 'FAIL'}: {n_skills} skill(s), "
          f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())

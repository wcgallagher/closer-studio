#!/usr/bin/env python3
"""Zero-context checker for a skill folder.

Fails (exit 1) when:
  - SKILL.md frontmatter lacks name or description
  - a relative path or script referenced in backticks does not exist (checked from the skill folder,
    then from the repo root found by walking up to a .git folder)
  - a number, dollar figure or percentage in SKILL.md has no matching row in AUDIT.md

Usage: python3 audit_skill.py path/to/SKILL.md [--repo-root DIR]
"""

import re
import sys
from pathlib import Path

NUM = re.compile(r"\$\d[\d,.]*\s?[KMB]?|\b\d+(?:\.\d+)?\s?%|\b\d{2,}(?:[,.]\d+)*\b")
PATH = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|sh|js|json|md|txt|ass|yaml|yml|toml))`")
# numbers that are formatting, not claims (years in dates, sizes in style specs, exit codes)
IGNORE_NUM = re.compile(r"^(?:\d{1,3}|20\d\d)$")


def find_root(start: Path) -> Path | None:
    for p in [start, *start.parents]:
        if (p / ".git").exists() or ((p / "tools").is_dir() and (p / "skills").is_dir()):   # a clone, or a ZIP download of the kit
            return p
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    skill = Path(sys.argv[1]).resolve()
    if skill.is_dir():                      # a skill folder works too
        skill = skill / "SKILL.md"
    folder = skill.parent
    root = Path(sys.argv[sys.argv.index("--repo-root") + 1]).resolve() if "--repo-root" in sys.argv \
        else find_root(folder)
    text = skill.read_text(encoding="utf-8")
    problems = []

    if "\u2014" in text:
        problems.append("em dash in SKILL.md (use a comma, a period or parentheses)")
    for w in ("delve", "tapestry", "testament", "pivotal", "seamless", "showcase", "underscore"):
        if re.search(rf"\b{w}\b", text, re.I):
            problems.append(f"banned word: {w}")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        problems.append("no YAML frontmatter")
    else:
        for key in ("name", "description"):
            if not re.search(rf"^{key}:\s*\S", fm.group(1), re.M):
                problems.append(f"frontmatter missing {key}")

    body = text[fm.end():] if fm else text
    for ref in sorted(set(PATH.findall(body))):
        if "<" in ref or ref.startswith("path/"):
            continue
        hits = [base / ref for base in (folder, root) if base and (base / ref).exists()]
        if not hits:
            problems.append(f"referenced path not found: {ref}")

    audit = folder / "AUDIT.md"
    audit_text = audit.read_text(encoding="utf-8") if audit.exists() else ""
    nums = {n.strip() for n in NUM.findall(body)}
    claims = sorted(n for n in nums if not IGNORE_NUM.match(n.replace(",", "")))
    missing = [n for n in claims if n not in audit_text]
    if claims and not audit.exists():
        problems.append(f"AUDIT.md missing but SKILL.md states {len(claims)} figures")
    elif missing:
        problems.append("figures with no AUDIT.md row: " + ", ".join(missing))

    if problems:
        print(f"AUDIT FAIL: {skill}")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"AUDIT PASS: {skill} ({len(claims)} figures sourced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

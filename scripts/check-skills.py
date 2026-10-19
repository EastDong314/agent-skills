#!/usr/bin/env python3
"""Static checks for the skills in this repo.

Checks per `skills/<name>/SKILL.md`:
  1. YAML frontmatter has `name` and `description`; `name` equals the directory.
  2. No absolute `/home/...` paths (breaks portability).
  3. Every `references/...`, `scripts/...`, `agents/...` path mentioned exists.
  4. Every bundled `.py` file compiles.

Exit code 1 if any error is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
RESOURCE_RE = re.compile(r"(?<![\w/])(references|scripts|agents)/[A-Za-z0-9._/\-]+")
HOME_PATH_RE = re.compile(r"/home/[A-Za-z0-9._-]+")
NAME_RE = re.compile(r"^name:\s*(.+)$", re.M)
DESC_RE = re.compile(r"^description:\s*(.+)$", re.M)


def frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def check_skill(skill: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill.name}: 缺少 SKILL.md"]

    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if not fm:
        errors.append(f"{skill.name}: 缺少 YAML frontmatter")
        return errors

    name_m = NAME_RE.search(fm)
    if not name_m:
        errors.append(f"{skill.name}: frontmatter 缺少 name")
    elif name_m.group(1).strip().strip("'\"") != skill.name:
        errors.append(
            f"{skill.name}: frontmatter name={name_m.group(1).strip()} 与目录名不一致"
        )

    desc = DESC_RE.search(fm)
    if not desc or len(fm.split("description:", 1)[1].strip()) < 20:
        errors.append(f"{skill.name}: frontmatter 缺少有效 description")

    for bad in HOME_PATH_RE.findall(text):
        errors.append(f"{skill.name}: SKILL.md 含硬编码绝对路径 {bad}")

    docs = [skill_md]
    refs = skill / "references"
    if refs.is_dir():
        docs += sorted(refs.glob("*.md"))
    for md in docs:
        content = md.read_text(encoding="utf-8")
        for rel in RESOURCE_RE.findall(content):
            candidate = skill / rel
            if not candidate.exists():
                errors.append(f"{md.relative_to(skill)}: 引用了不存在的 {rel}")

    for py in skill.rglob("*.py"):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except SyntaxError as exc:
            errors.append(f"{py.relative_to(skill)}: Python 语法错误: {exc}")

    return errors


def main() -> int:
    if not SKILLS.is_dir():
        print("找不到 skills/ 目录", file=sys.stderr)
        return 1

    total = 0
    failed = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        total += 1
        errors = check_skill(skill)
        if errors:
            failed += 1
            print(f"✗ {skill.name}")
            for e in errors:
                print(f"    - {e}")
        else:
            print(f"✓ {skill.name}")

    print(f"\n{total - failed}/{total} 个 skill 通过检查")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

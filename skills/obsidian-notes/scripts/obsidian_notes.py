#!/usr/bin/env python
"""Vault-scoped helper for Ricky's Obsidian notes."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import secrets
from datetime import date
from pathlib import Path
from urllib.parse import quote

DEFAULT_VAULT = Path(os.environ.get("OBSIDIAN_VAULT", Path.home() / "workspace" / "notes")).expanduser()
OBSIDIAN_FLATPAK_ID = "md.obsidian.Obsidian"
DEFAULT_INDEX = Path("技术/00-System/index.md")
DEFAULT_LOG = Path("技术/00-System/log.md")

# Agent instruction files are tooling, not knowledge notes: keep them out of the
# generated index and the lint pass. Otherwise the root AGENTS.md and a nested
# AGENTS.md collide on one wiki-link target and both get flagged for missing
# frontmatter / related section.
AGENT_INSTRUCTION_FILES = {"agents.md", "claude.md"}
CANVAS_SIDES = {"top", "right", "bottom", "left"}
CANVAS_ENDS = {"none", "arrow"}
CANVAS_NODE_TYPES = {"text", "file", "link", "group"}
CANVAS_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def resolve_note(vault: Path, rel_path: str) -> Path:
    path = resolve_vault_path(vault, rel_path)
    if path.suffix == "":
        path = path.with_suffix(".md")
    return path


def resolve_vault_path(vault: Path, rel_path: str) -> Path:
    vault = vault.resolve()
    path = (vault / rel_path).resolve()
    if not str(path).lower().startswith(str(vault).lower() + os.sep) and path != vault:
        raise SystemExit(f"Refusing path outside vault: {path}")
    return path


def frontmatter(title: str, tags: list[str] | None) -> str:
    today = date.today().isoformat()
    clean_tags = [tag.strip().lstrip("#") for tag in tags or [] if tag.strip()]
    tag_text = "[" + ", ".join(clean_tags) + "]" if clean_tags else "[]"
    return (
        "---\n"
        f"title: {title}\n"
        "aliases: []\n"
        f"tags: {tag_text}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        "---\n\n"
    )


def note_title(path: Path, explicit: str | None) -> str:
    return explicit or path.stem


def cmd_list(args: argparse.Namespace) -> int:
    vault = args.vault.resolve()
    files = sorted(str(path.relative_to(vault)) for path in vault.rglob("*.md"))
    if args.json:
        print(json.dumps(files, ensure_ascii=False, indent=2))
    else:
        print("\n".join(files))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    vault = args.vault.resolve()
    needle = args.query.lower()
    results = []
    for path in vault.rglob("*.md"):
        rel = str(path.relative_to(vault))
        title_match = needle in path.stem.lower() or needle in rel.lower()
        text = path.read_text(encoding="utf-8", errors="replace")
        content_match = needle in text.lower()
        if title_match or content_match:
            lines = []
            for idx, line in enumerate(text.splitlines(), start=1):
                if needle in line.lower():
                    lines.append({"line": idx, "text": line[:240]})
                    if len(lines) >= args.max_lines:
                        break
            results.append({"path": rel, "title_match": title_match, "matches": lines})
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(item["path"])
            for match in item["matches"]:
                print(f"  {match['line']}: {match['text']}")
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    if path.suffix == "":
        path = path.with_suffix(".md")
    text = path.read_text(encoding="utf-8")
    if args.json:
        print(json.dumps({"path": str(path), "content": text}, ensure_ascii=False, indent=2))
    else:
        print(text)
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    path = resolve_note(args.vault, args.path)
    if path.exists() and not args.force:
        raise SystemExit(f"Note already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = args.body or f"# {note_title(path, args.title)}\n\n## Related\n\n"
    text = frontmatter(note_title(path, args.title), split_tags(args.tags)) + body
    path.write_text(text, encoding="utf-8", newline="\n")
    print(path)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    path = resolve_note(args.vault, args.path)
    if not path.exists():
        raise SystemExit(f"Note does not exist: {path}")
    path.write_text(args.body, encoding="utf-8", newline="\n")
    print(path)
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    path = resolve_note(args.vault, args.path)
    if not path.exists():
        raise SystemExit(f"Note does not exist: {path}")
    if not args.yes:
        raise SystemExit("Deletion requires --yes")
    path.unlink()
    print(path)
    return 0


def cmd_open(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    if path.suffix == "":
        path = path.with_suffix(".md")
    vault_name = args.vault.resolve().name
    rel = path.relative_to(args.vault.resolve()).as_posix()
    uri = f"obsidian://open?vault={quote(vault_name)}&file={quote(rel)}"
    try:
        subprocess.Popen(["flatpak", "run", OBSIDIAN_FLATPAK_ID, uri], close_fds=True)
    except FileNotFoundError:
        subprocess.Popen(["xdg-open", uri], close_fds=True)
    print(uri)
    return 0


def first_heading_or_title(text: str, fallback: str) -> str:
    frontmatter_title = re.search(r"(?m)^title:\s*['\"]?(.+?)['\"]?\s*$", text)
    if frontmatter_title:
        return frontmatter_title.group(1).strip()
    heading = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if heading:
        return heading.group(1).strip()
    return fallback


def first_summary_line(text: str) -> str:
    in_frontmatter = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith((">", "-", "*", "```")):
            continue
        return stripped[:160]
    return ""


def wiki_target(path: Path) -> str:
    return path.stem


def cmd_index(args: argparse.Namespace) -> int:
    vault = args.vault.resolve()
    index_path = resolve_note(args.vault, str(args.path))
    rows = []
    for path in sorted(vault.rglob("*.md")):
        if path.resolve() == index_path.resolve():
            continue
        rel = path.relative_to(vault)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if path.name.lower() in AGENT_INSTRUCTION_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rows.append(
            {
                "path": rel.as_posix(),
                "title": first_heading_or_title(text, path.stem),
                "summary": first_summary_line(text),
                "link": wiki_target(path),
            }
        )
    lines = [
        "---",
        "title: Knowledge Index",
        "aliases: [Index]",
        "tags: [system, index]",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        "# Knowledge Index",
        "",
        "| Note | Path | Summary |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        summary = row["summary"].replace("|", "\\|")
        lines.append(f"| [[{row['link']}|{row['title']}]] | `{row['path']}` | {summary} |")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(index_path)
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    log_path = resolve_note(args.vault, str(args.path))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(
            "---\n"
            "title: Knowledge Base Log\n"
            "aliases: [Log]\n"
            "tags: [system, log]\n"
            f"created: {date.today().isoformat()}\n"
            "---\n\n"
            "# Knowledge Base Log\n\n",
            encoding="utf-8",
            newline="\n",
        )
    entry = f"## [{date.today().isoformat()}] {args.kind} | {args.title}\n\n{args.body.strip()}\n\n"
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(entry)
    print(log_path)
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    vault = args.vault.resolve()
    notes = []
    stems: dict[str, list[str]] = {}
    all_text = ""
    for path in sorted(vault.rglob("*.md")):
        rel = path.relative_to(vault)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if path.name.lower() in AGENT_INSTRUCTION_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel_text = rel.as_posix()
        notes.append({"path": rel_text, "stem": path.stem, "text": text})
        stems.setdefault(path.stem.lower(), []).append(rel_text)
        all_text += "\n" + text

    issues = []
    for note in notes:
        text = note["text"]
        is_system_note = note["path"].lower() in {
            DEFAULT_INDEX.as_posix().lower(),
            DEFAULT_LOG.as_posix().lower(),
        }
        if not text.startswith("---"):
            issues.append({"path": note["path"], "type": "missing-frontmatter"})
        if not is_system_note and "[[" not in text:
            issues.append({"path": note["path"], "type": "no-wiki-links"})
        related_heading_re = r"(?mi)^##\s+(related|links|相关链接)\s*$"
        if not is_system_note and not re.search(related_heading_re, text):
            issues.append({"path": note["path"], "type": "missing-related-section"})
        inbound = len(re.findall(r"\[\[" + re.escape(note["stem"]) + r"(\||#|\]\])", all_text, re.I))
        if not is_system_note and inbound <= 1:
            issues.append({"path": note["path"], "type": "possible-orphan"})

    for stem, paths in stems.items():
        if len(paths) > 1:
            issues.append({"path": ", ".join(paths), "type": "duplicate-title-stem", "title": stem})

    if args.json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        for issue in issues:
            detail = f" ({issue['title']})" if "title" in issue else ""
            print(f"{issue['type']}: {issue['path']}{detail}")
    return 0


def validate_canvas_payload(data: object) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [{"type": "canvas-root", "message": "Canvas root must be a JSON object"}]
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list):
        issues.append({"type": "canvas-nodes", "message": "nodes must be an array"})
        nodes = []
    if not isinstance(edges, list):
        issues.append({"type": "canvas-edges", "message": "edges must be an array"})
        edges = []
    ids: set[str] = set()
    node_ids: set[str] = set()
    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            issues.append({"type": "canvas-node", "message": f"node {idx} must be an object"})
            continue
        node_id = str(node.get("id", ""))
        if not re.fullmatch(r"[0-9a-f]{16}", node_id):
            issues.append({"type": "canvas-node-id", "message": f"node {idx} has invalid id {node_id!r}"})
        if node_id in ids:
            issues.append({"type": "canvas-duplicate-id", "message": f"duplicate id {node_id}"})
        ids.add(node_id)
        node_ids.add(node_id)
        node_type = node.get("type")
        if node_type not in CANVAS_NODE_TYPES:
            issues.append({"type": "canvas-node-type", "message": f"node {node_id} has invalid type {node_type!r}"})
        for key in ("x", "y", "width", "height"):
            if not isinstance(node.get(key), int):
                issues.append({"type": "canvas-node-field", "message": f"node {node_id} missing integer {key}"})
        if node_type == "text" and not isinstance(node.get("text"), str):
            issues.append({"type": "canvas-text-node", "message": f"text node {node_id} missing text"})
        if node_type == "file" and not isinstance(node.get("file"), str):
            issues.append({"type": "canvas-file-node", "message": f"file node {node_id} missing file"})
        if node_type == "link" and not isinstance(node.get("url"), str):
            issues.append({"type": "canvas-link-node", "message": f"link node {node_id} missing url"})
        color = node.get("color")
        if color is not None and str(color) not in {"1", "2", "3", "4", "5", "6"} and not CANVAS_COLOR_RE.match(str(color)):
            issues.append({"type": "canvas-color", "message": f"node {node_id} has invalid color {color!r}"})

    for idx, edge in enumerate(edges):
        if not isinstance(edge, dict):
            issues.append({"type": "canvas-edge", "message": f"edge {idx} must be an object"})
            continue
        edge_id = str(edge.get("id", ""))
        if not re.fullmatch(r"[0-9a-f]{16}", edge_id):
            issues.append({"type": "canvas-edge-id", "message": f"edge {idx} has invalid id {edge_id!r}"})
        if edge_id in ids:
            issues.append({"type": "canvas-duplicate-id", "message": f"duplicate id {edge_id}"})
        ids.add(edge_id)
        for key in ("fromNode", "toNode"):
            target = edge.get(key)
            if target not in node_ids:
                issues.append({"type": "canvas-dangling-edge", "message": f"edge {edge_id} has invalid {key} {target!r}"})
        for key in ("fromSide", "toSide"):
            if edge.get(key) is not None and edge.get(key) not in CANVAS_SIDES:
                issues.append({"type": "canvas-edge-side", "message": f"edge {edge_id} has invalid {key}"})
        for key in ("fromEnd", "toEnd"):
            if edge.get(key) is not None and edge.get(key) not in CANVAS_ENDS:
                issues.append({"type": "canvas-edge-end", "message": f"edge {edge_id} has invalid {key}"})
    return issues


def cmd_validate_canvas(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    data = json.loads(path.read_text(encoding="utf-8"))
    issues = validate_canvas_payload(data)
    if args.json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        if not issues:
            print(f"OK: {path}")
        for issue in issues:
            print(f"{issue['type']}: {issue['message']}")
    return 1 if issues and args.fail_on_issue else 0


def cmd_create_canvas(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    if path.suffix == "":
        path = path.with_suffix(".canvas")
    if path.exists() and not args.force:
        raise SystemExit(f"Canvas already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"nodes": [], "edges": []}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(path)
    return 0


def parse_yaml_text(text: str) -> object:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit("PyYAML is required for base validation. Install with: python -m pip install PyYAML") from exc
    return yaml.safe_load(text)


def validate_base_payload(data: object) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [{"type": "base-root", "message": "Base root must be a YAML mapping"}]
    if "views" not in data:
        issues.append({"type": "base-views", "message": "Base should define at least one view"})
    elif not isinstance(data["views"], list):
        issues.append({"type": "base-views", "message": "views must be a list"})
    else:
        formulas = set((data.get("formulas") or {}).keys()) if isinstance(data.get("formulas"), dict) else set()
        for idx, view in enumerate(data["views"]):
            if not isinstance(view, dict):
                issues.append({"type": "base-view", "message": f"view {idx} must be a mapping"})
                continue
            if view.get("type") not in {"table", "cards", "list", "map"}:
                issues.append({"type": "base-view-type", "message": f"view {idx} has invalid type {view.get('type')!r}"})
            order = view.get("order", [])
            if order is not None and not isinstance(order, list):
                issues.append({"type": "base-view-order", "message": f"view {idx} order must be a list"})
                order = []
            for item in order:
                if isinstance(item, str) and item.startswith("formula.") and item.removeprefix("formula.") not in formulas:
                    issues.append({"type": "base-missing-formula", "message": f"view {idx} references undefined {item}"})
    return issues


def cmd_validate_base(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    data = parse_yaml_text(path.read_text(encoding="utf-8"))
    issues = validate_base_payload(data)
    if args.json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        if not issues:
            print(f"OK: {path}")
        for issue in issues:
            print(f"{issue['type']}: {issue['message']}")
    return 1 if issues and args.fail_on_issue else 0


def cmd_create_base(args: argparse.Namespace) -> int:
    path = resolve_vault_path(args.vault, args.path)
    if path.suffix == "":
        path = path.with_suffix(".base")
    if path.exists() and not args.force:
        raise SystemExit(f"Base already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    title = args.name or path.stem
    content = (
        "filters:\n"
        "  and:\n"
        "    - 'file.ext == \"md\"'\n"
        "\n"
        "views:\n"
        "  - type: table\n"
        f"    name: \"{title}\"\n"
        "    order:\n"
        "      - file.name\n"
        "      - file.mtime\n"
    )
    path.write_text(content, encoding="utf-8", newline="\n")
    print(path)
    return 0


def canvas_id() -> str:
    return secrets.token_hex(8)


def split_tags(value: str | None) -> list[str]:
    if not value:
        return []
    return [part for part in re.split(r"[, ]+", value) if part]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--max-lines", type=int, default=5)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("read")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("create")
    p.add_argument("path")
    p.add_argument("--title")
    p.add_argument("--tags")
    p.add_argument("--body")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("update")
    p.add_argument("path")
    p.add_argument("--body", required=True)
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("delete")
    p.add_argument("path")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("open")
    p.add_argument("path")
    p.set_defaults(func=cmd_open)

    p = sub.add_parser("index")
    p.add_argument("--path", type=Path, default=DEFAULT_INDEX)
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("log")
    p.add_argument("kind", choices=["ingest", "query", "lint", "update", "refactor"])
    p.add_argument("title")
    p.add_argument("--body", required=True)
    p.add_argument("--path", type=Path, default=DEFAULT_LOG)
    p.set_defaults(func=cmd_log)

    p = sub.add_parser("lint")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("create-canvas")
    p.add_argument("path")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create_canvas)

    p = sub.add_parser("validate-canvas")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-issue", action="store_true")
    p.set_defaults(func=cmd_validate_canvas)

    p = sub.add_parser("create-base")
    p.add_argument("path")
    p.add_argument("--name")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_create_base)

    p = sub.add_parser("validate-base")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-issue", action="store_true")
    p.set_defaults(func=cmd_validate_base)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.vault.exists():
        raise SystemExit(f"Vault does not exist: {args.vault}")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

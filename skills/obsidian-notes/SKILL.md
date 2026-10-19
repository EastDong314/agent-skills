---
name: obsidian-notes
description: >
  管理 Ricky 的本地 Obsidian 知识库（默认 $HOME/workspace/notes）：创建、读取、更新、删除、搜索、重构、入库(ingest)、体检(lint)、建索引与整理笔记。当用户要求管理 Obsidian 笔记、知识库内容、日记、项目笔记、资料入库(source-to-wiki)、backlinks、tags、YAML frontmatter、Properties、Bases、Dataview 字段或查询、wiki 链接、嵌入、callout、canvas、网页剪藏，或用本地 Obsidian 应用/CLI 打开笔记时使用。 |
  Create, read, update, delete, search, refactor, ingest, lint, index, and organize Ricky's local Obsidian vault at $HOME/workspace/notes (override with OBSIDIAN_VAULT). Use when an AI coding agent is asked to manage Obsidian notes, knowledge-base content, daily notes, project notes, source-to-wiki ingestion, backlinks, tags, YAML frontmatter, Properties, Bases, Dataview fields or queries, wiki links, embeds, callouts, canvases, web clipping, or to open notes in the local Obsidian app/CLI.
---

# Obsidian Notes

## Operating Context

Use the local vault at `${OBSIDIAN_VAULT:-$HOME/workspace/notes}`. Treat it as a user-owned knowledge base and a Markdown codebase: preserve unrelated edits, avoid bulk rewrites unless requested, and keep note filenames and links Obsidian-friendly.

This vault is normally the agent's workspace root, so ordinary note work can use the built-in file tools (Codex: `read`/`apply_patch`; DSH and pi: `read`/`edit`/`write`). For anything outside the vault, ask before writing.

This skill is one bundle shared by Codex, pi, and DSH. Pick the base directory that matches the current agent, then use `$HELPER` in every command below:

```bash
# DSH (canonical source copy)
export SKILL_DIR="$HOME/.dsh/skills/obsidian-notes"
# Codex
# export SKILL_DIR="$HOME/.codex/skills/obsidian-notes"
# pi
# export SKILL_DIR="$HOME/.pi/agent/skills/obsidian-notes"

export HELPER="$SKILL_DIR/scripts/obsidian_notes.py"
python3 "$HELPER" --help
```

If `SKILL_DIR` was never exported in the current shell, either export it again per command or resolve `scripts/obsidian_notes.py` against the skill base directory the harness reports for this skill. Use `python3` (the helper is standard-library only; fall back to `python` only if `python3` is absent).

Prefer this bundled helper for deterministic CRUD, index, log, lint, Bases, and Canvas operations. It defaults to the vault and refuses paths outside it.

Use the local Obsidian app or the `obsidian://` URI scheme to open notes when useful. On Linux Flatpak the app id is `md.obsidian.Obsidian`; there is normally no `obsidian` binary on `PATH`.

This skill is a local, vault-specific superset of the patterns in `kepano/obsidian-skills`: Obsidian Flavored Markdown, Bases, JSON Canvas, CLI usage, and clean web extraction. Keep those domains in one workflow so vault operations remain scoped to `${OBSIDIAN_VAULT:-$HOME/workspace/notes}`.

## Knowledge Base Model

Use a three-layer model for larger knowledge work:

- Raw sources: user-provided articles, PDFs, clippings, meeting notes, screenshots, or transcripts. Treat these as source-of-truth inputs; do not rewrite or delete them unless explicitly asked.
- Wiki notes: structured Markdown pages that the agent may create and maintain by summarizing, synthesizing, cross-linking, and updating.
- Schema: this skill plus vault-local convention notes under `技术/00-System/` and the Obsidian guidance folder. Search for notes about vault usage, taxonomy, and Obsidian conventions before non-trivial changes.

Vault-local schema notes worth reading first: `AGENTS.md` (vault root, vault-wide rules), `技术/AGENTS.md` (技术/ local rules), `技术/00-System/目录结构说明.md`, `技术/00-System/全局维护规则.md`, `技术/00-System/分类与标签规范.md`, `技术/00-System/知识库使用说明.md`, `技术/00-System/文档模板说明.md`, and `技术/10-个人效率与环境/Obsidian/Obsidian知识管理使用规范.md`.

Known vault conventions to honor:

- Content is written in Chinese; notes are Markdown with YAML frontmatter including at least `tags` and `related`, and usually `title`/`aliases`/`created`/`updated`/`type`/`status`/`source`.
- Root folders are `AI/` (main knowledge base, numbered sections), plus `开发/`, `日记/`, `零星想法/`, `项目/`.
- Unsure classification belongs in `98-待整理`; deprecated content belongs in `99-归档`. Create those folders only when something actually needs them.
- Prefer updating an existing high-value note over overwriting it; if a safe merge is impossible, create a new file with a "待合并" suffix.

For non-trivial work, read the relevant schema notes first. The goal is compounding knowledge: update existing pages, links, index entries, and logs so future sessions do not rediscover the same context from scratch.

## Workflow

1. Clarify the operation from the user's request: create, read, update, delete, search, ingest, query, lint, organize, open, create a Base, create a Canvas, clip a web source, or debug Obsidian behavior.
2. Inspect existing notes before changing anything:
   - Use `rg` in Bash, or the agent's own content/path search tools, for content and path search.
   - Use the helper's `search`, `read`, or `list` commands for vault-scoped paths.
   - Read vault schema notes when structure, taxonomy, or long-term maintenance matters.
   - Check `.obsidian/` only when app configuration matters.
3. Preserve Obsidian semantics:
   - Use wiki links like `[[Target Note]]` or `[[Target Note|Alias]]` for internal references.
   - Use heading links `[[Target Note#Heading]]` and block links `[[Target Note#^block-id]]` when the user needs precise references.
   - Use tags in frontmatter for stable classification; use inline `#tags` only when they are part of prose.
   - Maintain YAML frontmatter for metadata, dates, aliases, status, source, project, area, model, host, and next actions.
   - Prefer Obsidian Properties and Bases-compatible frontmatter for structured fields. Use Dataview inline fields such as `status:: active` only when the user explicitly asks for Dataview queries, inline fields, or a Dataview dashboard.
   - Prefer relative embeds `![[file.png]]` or `![[Note#Heading]]` when embedding vault content.
   - Use callouts only for content that benefits from visual emphasis: summaries, warnings, examples, decisions, todos, and questions.
4. Make scoped edits with the agent's patch/edit tool (Codex: `apply_patch`; DSH and pi: `edit`), or use `write`/the helper for whole-note create or replace. Read a file before editing or replacing it.
5. For durable changes, update or regenerate the index and append a log entry.
6. Verify after edits by reading the changed file, checking links/search results, validating `.base` or `.canvas` files when present, and optionally opening the note in Obsidian.

## Note Quality Rules

For new notes, create notes that are useful inside Obsidian, not plain Markdown dumps:

- Start with YAML frontmatter unless the target folder has a clear contrary convention.
- Include `aliases` when the concept has alternate names.
- Include `tags` that match existing vault taxonomy where possible.
- Add a concise first paragraph that states what the note is.
- Add sections with headings that make backlinking possible.
- Add `## 相关链接` or `## Links` with wiki links to relevant existing notes. Match the existing localized heading the target folder already uses: numbered `AI/` folders use `## 相关链接`, project notes may use either.
- Put structured fields in YAML frontmatter by default so Obsidian Properties and Bases can edit, sort, and filter them. Do not duplicate the same field as both frontmatter and `key:: value` in the body unless the user requests Dataview inline fields.
- For project or task notes, include actionable status and next-step fields.
- For evergreen knowledge notes, link claims to source notes and related concepts.

Read `references/obsidian-patterns.md` (under `$SKILL_DIR`) when creating new note templates, repairing note structure, or deciding how to use frontmatter, tags, backlinks, Dataview, index files, logs, and source ingestion.

## Obsidian Markdown Features

Use these syntax features when they make the note more useful inside Obsidian:

- Wikilinks: `[[Note]]`, `[[Note|Alias]]`, `[[Note#Heading]]`, `[[Note#^block-id]]`, `[[#Same-note heading]]`.
- Embeds: `![[Note]]`, `![[Note#Heading]]`, `![[image.png|300]]`, `![[document.pdf#page=3]]`, `![[Canvas.canvas]]`, `![[View.base#View Name]]`.
- Callouts: `> [!note]`, `> [!warning] Title`, `> [!todo]- Collapsed`, with nested quoted lines for content.
- Comments: `%%hidden text%%` or block comments for agent-only annotations that should not render.
- Highlight/math/diagrams: `==highlight==`, inline `$math$`, block `$$math$$`, and fenced `mermaid`.
- Footnotes: `[^1]` references, definitions, and inline footnotes.

Do not over-format notes. Prefer normal Markdown until an Obsidian extension improves navigation, retrieval, or rendering.

## Bases

Use `.base` files when the user wants database-like views of notes, task lists, reading lists, project dashboards, filtered indexes, or property-driven tables/cards/lists/maps.

Base files are YAML. Build them around:

- `filters`: global and view-specific expressions such as `file.hasTag("project")`, `file.inFolder("Daily Notes")`, `status == "active"`.
- `formulas`: computed fields such as days until due, status labels, word estimates, or derived links.
- `properties`: display names and configuration for note, file, and formula fields.
- `summaries`: aggregate formulas like Average, Sum, Min, Max, Latest, Checked, Empty, Filled, Unique.
- `views`: table, cards, list, or map views with explicit `order`.

Rules:

- Quote filter and formula expressions, especially when they contain `:`, `#`, brackets, comparison operators, or nested quotes.
- Wrap formulas containing double quotes in single quotes: `'if(done, "Yes", "No")'`.
- Date subtraction returns a duration. Access `.days`, `.hours`, etc. before numeric functions.
- Guard optional properties with `if(property, expression, fallback)`.
- Validate after editing: `python3 "$HELPER" validate-base "Dashboards/Projects.base"`.

## JSON Canvas

Use `.canvas` files when the user asks for a visual map, research board, flowchart, dependency map, project overview, or canvas.

Canvas files are JSON with top-level `nodes` and `edges` arrays:

- Nodes require `id`, `type`, `x`, `y`, `width`, and `height`.
- Node types are `text`, `file`, `link`, and `group`.
- Edges require `id`, `fromNode`, and `toNode`; optional sides are `top`, `right`, `bottom`, `left`.
- Generate unique 16-character lowercase hex IDs.
- Use real newlines in JSON string values, not literal `\n` unless the text should display those characters.
- Leave 50-100px between nodes, align to a grid, and keep group nodes large enough to contain their children.
- Validate after editing: `python3 "$HELPER" validate-canvas "Maps/Topic.canvas"`.

## Web Clipping And Source Extraction

When a user provides a URL to ingest into the vault:

- Prefer `defuddle parse <url> --md` when a local `defuddle` command exists; it extracts readable Markdown and removes navigation clutter.
- `defuddle` is not installed by default here; check first, otherwise use the agent's web fetch/search tools, then save only durable facts and links into the vault.
- Do not use Defuddle for URLs that already point to raw Markdown.
- Preserve the source URL, author/date if available, retrieval date, and processing status in frontmatter.
- For long sources, create a source summary note and update durable concept/project/entity notes instead of dumping the whole article into the wiki layer.

## Obsidian CLI And App

When Obsidian is running and an `obsidian` command is available, use it for app-aware actions:

```bash
obsidian help
obsidian read file="My Note"
obsidian search query="term" limit=10
obsidian property:set name="status" value="done" file="My Note"
obsidian backlinks file="My Note"
obsidian daily:append content="- [ ] Follow up"
```

For plugin or theme debugging, prefer app-aware commands after code changes:

```bash
obsidian plugin:reload id=my-plugin
obsidian dev:errors
obsidian dev:console level=error
obsidian dev:screenshot path=screenshot.png
obsidian dev:dom selector=".workspace-leaf" text
```

If the CLI is not installed or Obsidian is not running, fall back to vault file operations and the `obsidian://` URI scheme. The helper's `open` command already handles the Flatpak app and URI fallback:

```bash
python3 "$HELPER" open "技术/00-System/index.md"
```

## Ingest, Query, and Lint

Use ingest behavior when the user provides a source or asks to add knowledge from an external artifact:

- Read the source and identify durable facts, decisions, concepts, entities, open questions, and contradictions.
- Search the vault for existing pages before creating new ones.
- Create a source summary note only if it will be useful later.
- Update relevant existing concept/project/entity notes, not just the new source page.
- Add backlinks and `related` entries so the new knowledge is reachable from existing notes.
- Append a log entry describing what was ingested and which pages changed.

Use query behavior when answering from the vault:

- Read index/schema notes first when available.
- Search and read relevant notes before answering.
- Cite local notes by wiki link or path in the answer.
- If the answer creates durable synthesis, offer to write it back as a note or update an existing note.

Use lint behavior for maintenance:

- Check for missing frontmatter, missing related sections, orphan notes, duplicate titles, stale claims, bad links, and important concepts that lack pages.
- Prefer reporting a focused repair plan before doing broad cleanup.
- For requested cleanup, repair links and metadata in small batches and log the pass.

## Helper Commands

The helper defaults to `${OBSIDIAN_VAULT:-$HOME/workspace/notes}` (`--vault` to override) and refuses paths outside the vault. Run `python3 "$HELPER" --help` for the full command list.

```bash
# Search titles and content
python3 "$HELPER" search "query"

# Read a note by relative path
python3 "$HELPER" read "AI/example.md"

# Create a note, including parent folders
python3 "$HELPER" create "AI/example.md" --title "Example" --tags project,active --body $'# Example\n\n...'

# Replace a note after inspecting it
python3 "$HELPER" update "AI/example.md" --body "...full markdown..."

# Delete only when the user explicitly asks
python3 "$HELPER" delete "AI/old-note.md" --yes

# Open a note in Obsidian
python3 "$HELPER" open "AI/example.md"

# Create and validate a Base
python3 "$HELPER" create-base "技术/00-System/active-projects.base" --name "Active Projects"
python3 "$HELPER" validate-base "技术/00-System/active-projects.base"

# Create and validate a Canvas
python3 "$HELPER" create-canvas "AI/Maps/project-overview.canvas"
python3 "$HELPER" validate-canvas "AI/Maps/project-overview.canvas"

# Regenerate a wiki-style index at 技术/00-System/index.md
python3 "$HELPER" index

# Append a parseable operation log entry at 技术/00-System/log.md
python3 "$HELPER" log ingest "Article Title" --body "Updated [[Target Note]] and created [[Source Summary]]."

# Run a basic health check
python3 "$HELPER" lint --json
```

Use `--json` on `list`, `search`, `read`, and `lint` when structured output is easier to consume.

## Deletion Safety

Delete notes only when the user clearly asks for deletion. Before deleting, search for backlinks to the target note title and filename stem. If backlinks exist, report them or update them if the user asked for a full cleanup.

Prefer moving obsolete notes to an archive folder (`99-归档`) if the user asks to "retire", "archive", or "deprecate" a note rather than delete it.

## Link and Refactor Safety

When renaming or moving notes:

- Update wiki links that reference the old title, including aliases and heading links.
- Search for Markdown links that point to the old relative path.
- Preserve aliases in frontmatter so old names remain discoverable.
- Verify with `rg "\[\[Old Name"` and `rg "Old Name.md"` after the change.

## Maintaining This Skill

This bundle is maintained in the public `agent-skills` repository (the copy you are reading). Install or refresh it with that repo's `install.sh`; do not hand-sync separate agent copies.

The helper reads `OBSIDIAN_VAULT` when set, otherwise `$HOME/workspace/notes`.

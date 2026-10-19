#!/usr/bin/env bash
# Install the skills in this repo into one or more agent skill directories.
# Idempotent: existing skills are moved to a timestamped backup before replace.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/agent-skills"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/agent-skills"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$STATE_DIR/backups/$STAMP"

TARGET_ARG="auto"
LINK=0
DRY=0
EXTERNAL=1
ONLY=""
EXTRA_DIRS=()

usage() {
  cat <<'EOF'
用法: ./install.sh [选项]

  -t, --target LIST     安装目标，逗号分隔: auto | all | agents | dsh | codex | pi | claude | opencode
                        默认 auto = agents + 本机已存在的 codex/pi/claude/opencode
  -d, --target-dir PATH 额外目标目录（可重复），例如 ~/.zcode/skills
  -o, --only LIST       只安装这些 skill（逗号分隔）
  -l, --link            用符号链接代替复制（适合本仓库长期作为源）
  -n, --dry-run         只打印，不落盘
      --no-external     跳过从 GitHub 拉取的外部 skill（book-to-skill）
  -h, --help            显示帮助

示例:
  ./install.sh                          # 装到 ~/.agents/skills 及已存在的 agent 目录
  ./install.sh -t dsh,codex -l          # 只装 DSH/Codex，用软链
  ./install.sh -o obsidian-notes        # 只装一个
EOF
}

die() { printf '错误: %s\n' "$*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }
warn() { printf '警告: %s\n' "$*" >&2; }

target_root() {
  case "$1" in
    agents)   printf '%s/.agents/skills\n' "$HOME" ;;
    dsh)      printf '%s/.dsh/skills\n' "$HOME" ;;
    codex)    printf '%s/.codex/skills\n' "$HOME" ;;
    pi)       printf '%s/.pi/agent/skills\n' "$HOME" ;;
    claude)   printf '%s/.claude/skills\n' "$HOME" ;;
    opencode) printf '%s/.opencode/skills\n' "$HOME" ;;
    *) die "未知目标: $1" ;;
  esac
}

list_skill_names() {
  local dir="$1" d
  for d in "$dir"/*/; do
    [ -f "$d/SKILL.md" ] && basename "$d"
  done
}

target_parent_exists() {
  local root; root="$(target_root "$1")"
  [ -d "$(dirname "$root")" ]
}

selected() {
  [ -z "$ONLY" ] && return 0
  case ",$ONLY," in
    *",$1,"*) return 0 ;;
    *) return 1 ;;
  esac
}

run() {
  if [ "$DRY" = 1 ]; then
    printf '  [dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

backup_existing() {
  local dest="$1" target="$2" name="$3"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    local b="$BACKUP_DIR/$target/$name"
    run mkdir -p "$(dirname "$b")"
    run mv "$dest" "$b"
    say "  已备份: $dest -> $b"
  fi
}

install_skill() {
  local src="$1" name="$2" root="$3" target="$4"
  [ -f "$src/SKILL.md" ] || { warn "$name 缺少 SKILL.md，跳过"; return 0; }
  local dest="$root/$name"

  if [ "$LINK" = 1 ]; then
    backup_existing "$dest" "$target" "$name"
    run mkdir -p "$root"
    run ln -s "$src" "$dest"
  else
    backup_existing "$dest" "$target" "$name"
    run mkdir -p "$dest"
    run cp -R "$src/." "$dest/"
    if [ "$DRY" = 0 ]; then
      rm -rf "$dest/.git" "$dest/.github"
      find "$dest" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
      find "$dest" -name '*.pyc' -delete 2>/dev/null || true
    fi
  fi
  if [ "$DRY" = 1 ]; then
    say "  [dry] $name -> $dest"
  else
    say "  ✓ $name -> $dest"
  fi
}

fetch_external() {
  local name="$1" repo="$2" ref="$3"
  local dir="$CACHE_DIR/sources/$name"

  if [ "$DRY" = 1 ]; then
    say "  [dry-run] git fetch $repo @ $ref -> $dir"
    return 0
  fi

  if [ -d "$dir/.git" ]; then
    if git -C "$dir" fetch -q --depth 1 origin "$ref"; then
      git -C "$dir" checkout -q --detach FETCH_HEAD
      say "  ✓ 更新 $name @ ${ref:0:12}"
    else
      warn "$name 拉取失败，使用缓存副本"
    fi
  else
    mkdir -p "$dir"
    git -C "$dir" init -q
    git -C "$dir" remote add origin "$repo"
    if ! git -C "$dir" fetch -q --depth 1 origin "$ref"; then
      # 某些仓库不支持按 SHA 浅拉，退回到默认分支
      git -C "$dir" fetch -q --depth 1 origin HEAD
    fi
    git -C "$dir" checkout -q --detach FETCH_HEAD
    say "  ✓ 克隆 $name @ ${ref:0:12}"
  fi
}

# ---------- 参数 ----------
while [ $# -gt 0 ]; do
  case "$1" in
    -t|--target) [ $# -ge 2 ] || die "$1 需要参数"; TARGET_ARG="$2"; shift 2 ;;
    -d|--target-dir) [ $# -ge 2 ] || die "$1 需要参数"; EXTRA_DIRS+=("$2"); shift 2 ;;
    -o|--only) [ $# -ge 2 ] || die "$1 需要参数"; ONLY="$2"; shift 2 ;;
    -l|--link) LINK=1; shift ;;
    -n|--dry-run) DRY=1; shift ;;
    --no-external) EXTERNAL=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "未知参数: $1（用 --help 查看用法）" ;;
  esac
done

case "$TARGET_ARG" in
  auto)
    TARGETS=(agents)
    for t in codex pi claude opencode; do
      target_parent_exists "$t" && TARGETS+=("$t")
    done
    ;;
  all)
    TARGETS=(agents dsh codex pi claude opencode)
    ;;
  *)
    IFS=',' read -r -a TARGETS <<< "$TARGET_ARG"
    ;;
esac

[ ${#TARGETS[@]} -gt 0 ] || die "没有可安装的目标"

say "仓库:   $REPO_DIR"
say "目标:"
for t in "${TARGETS[@]}"; do
  say "  - $t: $(target_root "$t")"
done
for d in "${EXTRA_DIRS[@]}"; do
  say "  - custom: $d"
done
say ""

# ---------- 本仓库自带 skill ----------
say "== 本仓库 skill =="
for src in "$REPO_DIR"/skills/*/; do
  [ -d "$src" ] || continue
  src="${src%/}"
  name="$(basename "$src")"
  selected "$name" || continue
  for t in "${TARGETS[@]}"; do
    install_skill "$src" "$name" "$(target_root "$t")" "$t"
  done
  for d in "${EXTRA_DIRS[@]}"; do
    install_skill "$src" "$name" "$d" custom
  done
done

# ---------- 外部 GitHub 来源 ----------
if [ "$EXTERNAL" = 1 ]; then
  say ""
  say "== 外部来源 (sources.tsv) =="
  while IFS=$'\t' read -r name repo ref subdir layout; do
    name="${name%$'\r'}"; repo="${repo%$'\r'}"; ref="${ref%$'\r'}"
    subdir="${subdir%$'\r'}"; layout="${layout%$'\r'}"
    [ -z "$name" ] && continue
    case "$name" in \#*) continue ;; esac
    # layout=repo 时 source 名就是 skill 名；tree 时由子目录名过滤
    if [ "$layout" = "repo" ]; then
      selected "$name" || continue
    fi

    if ! command -v git >/dev/null 2>&1; then
      warn "未找到 git，跳过外部 skill $name"
      continue
    fi

    say "-- $name ($repo @ ${ref:0:12})"
    fetch_external "$name" "$repo" "$ref" || { warn "跳过 $name"; continue; }

    if [ "$layout" = "repo" ]; then
      for t in "${TARGETS[@]}"; do
        install_skill "$CACHE_DIR/sources/$name" "$name" "$(target_root "$t")" "$t"
      done
      for d in "${EXTRA_DIRS[@]}"; do
        install_skill "$CACHE_DIR/sources/$name" "$name" "$d" custom
      done
    else
      for src in "$CACHE_DIR/sources/$name/$subdir"/*/; do
        [ -d "$src" ] || continue
        src="${src%/}"
        sname="$(basename "$src")"
        [ -f "$src/SKILL.md" ] || continue
        selected "$sname" || continue
        for t in "${TARGETS[@]}"; do
          install_skill "$src" "$sname" "$(target_root "$t")" "$t"
        done
        for d in "${EXTRA_DIRS[@]}"; do
          install_skill "$src" "$sname" "$d" custom
        done
      done
    fi
  done < "$REPO_DIR/sources.tsv"
fi

# DSH 同时扫描这两个根，同名会出现两份
if [ -d "$HOME/.agents/skills" ] && [ -d "$HOME/.dsh/skills" ]; then
  dups="$(comm -12 <(list_skill_names "$HOME/.agents/skills" | sort -u) <(list_skill_names "$HOME/.dsh/skills" | sort -u))"
  if [ -n "$dups" ]; then
    warn "DSH 会同时扫描 ~/.agents/skills 和 ~/.dsh/skills，以下同名 skill 可能被识别两次："
    printf '  - %s\n' $dups >&2
    warn "建议只保留一处：默认用 ~/.agents/skills；只用 DSH 时用 -t dsh。"
  fi
fi

say ""
if [ "$LINK" = 1 ]; then
  say "完成（符号链接模式：修改本仓库即对所有 agent 生效）"
else
  say "完成。重新打开会话后，agent 会重新扫描 skill 目录。"
fi
if [ -d "$BACKUP_DIR" ]; then
  say "旧版本备份: $BACKUP_DIR"
fi
say ""
say "book-to-skill 依赖自检（可选）:"
say "  python3 \"\$HOME/.agents/skills/book-to-skill/scripts/extract.py\" --check"

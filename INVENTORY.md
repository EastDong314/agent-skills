# 本机 Skill 清点

> 清点时间：2026-10-19。范围：`/home/ricky` 下所有 `SKILL.md` 与 agent skill 目录。
> 判定标准：**用户级、可迁移、算个人资产**的才收进本仓库；工具自带、市场缓存、项目内嵌的只记录不打包。

## 一、已纳入本仓库（10 个）

| Skill | 本机位置 | 来源 | 大小 | 备注 |
| --- | --- | --- | --- | --- |
| `obsidian-notes` | `~/.dsh/skills`、`~/.codex/skills`、`~/.pi/agent/skills` | 自研 | 60 KB | 三份副本，内容基本一致；Codex 版多一个 `agents/openai.yaml` |
| `minfadian` | `~/.agents/skills` | 自研 | 464 KB | 7 编 + 附则 + 条号速查，共 1260 条 |
| `ponytail-review` | `~/.dsh/skills` | 派生自 `DietrichGebert/ponytail` | 4 KB | 上游完整插件在 `~/.codex/plugins/cache`，这里是单 skill 改写版 |
| `workflow-diagnose` | `~/.codex/skills`、`~/.pi/agent/skills` | `EastDong314/AI-Project-Workflow-Template` | 8 KB | 两份一致 |
| `workflow-grill-with-docs` | 同上 | 同上 | 12 KB | |
| `workflow-implement` | 同上 | 同上 | 12 KB | |
| `workflow-plan-acceptance` | 同上 | 同上 | 12 KB | |
| `workflow-review-md` | 同上 | 同上 | 12 KB | 上游仓库工作区有未提交改动，本仓库保存的是**本机已安装版本** |
| `ruoyi-vue-pro-dev` | 同上 | 同上 | 36 KB | 7 个 reference 文件 |
| `book-to-skill` | `~/.agents/skills` | `virgiliojr94/book-to-skill`（git clone） | 5.0 MB | 第三方 MIT；按 commit `526f362` 安装，不 vendoring |

DSH 当前会话可见 4 个：`book-to-skill`、`minfadian`、`obsidian-notes`、`ponytail-review`。另外 6 个只装在 Codex/pi 目录，DSH 不扫描 `~/.codex/skills`。

## 二、本机存在但未纳入

### 2.1 工具自带（不属于个人资产）

- `~/.codex/skills/.system/`：`imagegen`、`openai-docs`、`review-agent`、`skill-creator`、`skill-installer` —— Codex 内置，随版本更新。
- `~/.codex/plugins/cache/`：`openai-bundled`、`openai-curated-remote`（github、plugin-management、work-pets）、`openai-primary-runtime`（spreadsheets、presentations、template-creator、documents、pdf）、`ponytail`、`diagram-design` —— Codex 插件市场缓存。
- `~/.codex/.tmp/`：插件市场安装/升级临时目录，含大量第三方插件 skill（adobe、cloudflare、canva 等），随时会被清理。
- `~/.cache/codex-runtimes/`：Codex 运行时内置插件。

### 2.2 Skill 市场缓存（不逐个展开）

- `~/.dsh/skills-management/market/` ← `https://gitcode.com/weibaohui/ntd-resource.git`
- `skills/` 下 **44 个**第三方合集（`anthropics-skills`、`ComposioHQ-awesome-claude-skills`、`kepano-obsidian-skills`、`DietrichGebert-ponytail` 等）
- 这是市场索引/缓存，不是"已安装"的个人 skill；DSH 启动时浅克隆更新（`skills-market-sync.json`）。

### 2.3 项目级 skill（跟随各自仓库，不进全局）

| 位置 | 内容 | 为什么排除 |
| --- | --- | --- |
| `~/workspace/tradingP/.codex/skills/` | 5 个 workflow skill + README | 项目自包含副本，已提交到该项目仓库 |
| `~/workspace/oilfield/.agents/skills/` | `review-plan`、`fix-plan`、`implement-plan` | 绑定 oilfield 项目的计划文档与契约；项目已 git 跟踪 |
| `~/workspace/rea/.agents/skills/` | `rea-changelog-update`、`rea-tool-design`、`reverse-engineer-anything` | 绑定 REA 项目；项目已 git 跟踪 |
| `~/workspace/AI-Project-Workflow-Template/skills/` | 上表 6 个 workflow/ruoyi skill 的上游 | 上游源仓库，避免双向复制 |
| `~/workspace/AI-Project-Workflow-Template/template/.codex/skills/` | 模板工程内的副本 | 同上 |
| `~/workspace/playground/fluxdown-调研/repo/.omp/skills/` | `main-worktree`、`release`（空目录） | 调研残留，无 `SKILL.md` |

### 2.4 重复副本

| Skill | 副本数 | 处理 |
| --- | --- | --- |
| `obsidian-notes` | 3 | 本仓库为唯一源；`install.sh` 覆盖三处，不再手工 sync |
| `workflow-*` + `ruoyi-vue-pro-dev` | 2（codex、pi） | 同上 |
| `book-to-skill` | 1 | 外部 clone，不在仓库里再存一份 |

## 三、结论

- 本机"全局可迁移"的 skill 实际是 **10 个**，其中 9 个已进 `skills/`，1 个（book-to-skill）由 `install.sh` 从上游按 commit 安装。
- 其余 100+ 个 `SKILL.md` 来自 Codex 内置、插件市场缓存、NTD 市场克隆、项目仓库，**都不应该复制进个人 skill 仓库**，否则版本和归属会乱。
- 项目级 skill 保持"谁的项目谁维护"；如果以后想全局化，先把它从项目里抽出来再放进本仓库。

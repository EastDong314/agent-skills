# agent-skills

一台机器上的个人 agent skill，收拢成一个可直接复制到新机器的仓库。

目标是：**新机器 `git clone` + 一条 `./install.sh`，DSH / Codex / pi 都能用上同一套 skill。**

## 快速开始

```bash
git clone https://github.com/EastDong314/agent-skills.git
cd agent-skills
./install.sh
```

默认行为：

- 安装到 `~/.agents/skills`（跨 agent 共享池，**DSH 会读这里**）
- 本机已存在 `~/.codex` / `~/.pi` / `~/.claude` / `~/.opencode` 时，同时装到各自目录
- 覆盖前把旧版本备份到 `~/.local/state/agent-skills/backups/<时间戳>/`
- 重新打开会话后生效（agent 在启动时扫描 skill 目录）

常用参数：

```bash
./install.sh --dry-run                 # 只预览
./install.sh -t dsh                    # 只装 DSH 私有目录 ~/.dsh/skills
./install.sh -t agents,codex -l        # 软链安装，改仓库即对所有 agent 生效
./install.sh -o obsidian-notes         # 只装一个 skill
./install.sh --no-external             # 不联网，跳过 book-to-skill
./install.sh -d ~/.zcode/skills        # 额外目标目录
```

`--help` 查看全部选项。

## 装到哪里

| `--target` | 目录 | 说明 |
| --- | --- | --- |
| `agents` | `~/.agents/skills` | 跨 agent 共享池；DSH、Copilot CLI、Amp、OpenClaw 等读取 |
| `dsh` | `~/.dsh/skills` | DSH 私有目录 |
| `codex` | `~/.codex/skills` | Codex |
| `pi` | `~/.pi/agent/skills` | pi（注意不是 `~/.pi/skills`） |
| `claude` | `~/.claude/skills` | Claude Code |
| `opencode` | `~/.opencode/skills` | OpenCode |
| `--target-dir PATH` | 自定义 | 任何其他 agent |

默认不装 `~/.dsh/skills`，因为 DSH 同时扫描 `~/.agents/skills`，两边都装会出现同名 skill。只用 DSH 的话用 `-t dsh`。

> 从旧布局迁移：如果 `~/.dsh/skills` 里已经有同名 skill，`install.sh` 会检测到重叠并警告；确认后把旧的那份删掉或移走，只保留一处。

## 仓库里有什么

### 本仓库直接维护（`skills/`）

| Skill | 用途 | 来源 |
| --- | --- | --- |
| `obsidian-notes` | 管理本地 Obsidian 知识库：CRUD、搜索、ingest、lint、索引、Bases、Canvas | 自研 |
| `minfadian` | 《民法典》1260 条原文逐字查询 | 自研（官方全文生成） |
| `ponytail-review` | 只追查过度设计的代码审查，一行一条发现 | 派生自 [DietrichGebert/ponytail](https://github.com/dietrichgebert/ponytail)（MIT） |
| `ruoyi-vue-pro-dev` | ruoyi-vue-pro / Yudao 开发约定（后端、Vue3、uni-app、SQL、权限） | 自研，上游 [AI-Project-Workflow-Template](https://github.com/EastDong314/AI-Project-Workflow-Template) |
| `workflow-grill-with-docs` | 先对齐仓库、文档、ADR，再规划 | 同上 |
| `workflow-plan-acceptance` | 生成 `.ai-workflow/{GOAL,PLAN,ACCEPTANCE}.md` | 同上 |
| `workflow-implement` | 按 `.ai-workflow` 状态执行实现 | 同上 |
| `workflow-review-md` | 按计划评审 diff，产出 `REVIEW.md` | 同上 |
| `workflow-diagnose` | 证据优先的 bug 诊断 | 同上 |

### 从 GitHub 按固定 commit 安装（`sources.tsv`）

| Skill | 上游 | 为什么不在仓库里 |
| --- | --- | --- |
| `book-to-skill` | [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill)（MIT） | 5 MB 的第三方完整仓库，含 docs/tests/evals；按 pin 的 commit 克隆更合适 |

安装时克隆到 `~/.cache/agent-skills/sources/`，再复制到各目标目录（不带 `.git`）。更新时改 `sources.tsv` 里的 ref，重新运行即可。

## 外部依赖

- `bash`、`git`、`python3`：安装脚本和 helper 需要
- `book-to-skill` 的文档解析依赖按需自检：

  ```bash
  python3 ~/.agents/skills/book-to-skill/scripts/extract.py --check
  ```

  PDF 文本解析至少要有 `pdftotext` / `pypdf` / `pdfminer.six` 之一；技术类 PDF 想要表格/公式保真需要 `docling`。
- `obsidian-notes` 默认 vault 是 `$HOME/workspace/notes`，可用 `OBSIDIAN_VAULT=/path/to/vault` 覆盖

## 维护

新增 skill：

```bash
mkdir -p skills/my-skill
$EDITOR skills/my-skill/SKILL.md   # 至少要有 name + description frontmatter
python3 scripts/check-skills.py
./install.sh -o my-skill
```

`scripts/check-skills.py` 会检查：frontmatter 是否齐全、name 是否与目录一致、有没有 `/home/xxx` 硬编码路径、引用的 `references/` `scripts/` 文件是否存在、Python 文件能否编译。

## 清点与评审

- [INVENTORY.md](INVENTORY.md)：本机所有 skill 的来源、位置、取舍（哪些没进仓库、为什么）
- [REVIEW.md](REVIEW.md)：逐项评审发现、修复情况、验证记录

## 许可与归属

- 本仓库自己的内容：MIT，见 [LICENSE](LICENSE)
- 第三方内容与来源：见 [NOTICE](NOTICE)
- `minfadian` 引用法律法规原文；法律法规不受著作权保护

仓库中的 skill 含有个人工作习惯与本地路径约定（已改为 `$HOME` / 环境变量），**不包含任何 token、密钥或服务器凭据**。

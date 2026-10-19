# 评审记录

> 对象：本仓库收拢的 10 个全局 skill + 安装脚本。时间：2026-10-19。
> 方法：逐个读 `SKILL.md` 与脚本、对比多份副本、静态检查、隔离 HOME 实装、依赖自检。
> 结论先行：**可以公开/可迁移**。9 个入库 skill 全部通过检查；1 个外部 skill 安装链路实测可用。

## 一、发现与处理

| # | 严重度 | 位置 | 发现 | 处理 |
| --- | --- | --- | --- | --- |
| R1 | 高 | `obsidian-notes` 三份副本 | 同一 skill 手工同步 `~/.dsh`、`~/.codex`、`~/.pi`；原维护说明写死路径 + `cp` 循环，漏同步就漂移 | 本仓库作为单一源；`install.sh` 统一分发；删掉手工 sync 段；三目标安装已实测 |
| R2 | 高 | `obsidian-notes`、`minfadian` | 19 处 `/home/ricky/...` 硬编码，换用户名/换机器直接坏 | vault 改为 `$HOME/workspace/notes` + `OBSIDIAN_VAULT` 覆盖；`minfadian` 的 skill 目录改从 `__file__` 推导；复检 0 处 |
| R3 | 中 | `book-to-skill` | 本机是 5 MB 完整 clone（含 `.git`/`docs`/`tests`/`evals`），且版本 `526f362` 落后上游 HEAD `a24e62f` | 不 vendoring；`sources.tsv` 按 SHA 克隆安装；提供 `extract.py --check` 自检；升级只需改 ref |
| R4 | 中 | 6 个 workflow/ruoyi skill | Codex 与 pi 各一份；上游 `AI-Project-Workflow-Template` 工作区有未提交改动，上游 HEAD 不一定等于本机版本 | 以**本机已安装版本**为快照入库并标注来源；`sources.tsv` 保留可切换到上游的注释行 |
| R5 | 低 | `ponytail-review` | 第三方 MIT 派生作品，仓库里没有版权声明 | 加 `NOTICE` + `THIRD-PARTY/ponytail-LICENSE` 全文 |
| R6 | 低 | 全部 `SKILL.md` | 描述中英混排、偏长（最长 774 字符） | 保留：description 是 agent 触发匹配的关键；DSH 目录只截断显示，不影响加载 |
| R7 | 低 | `install.sh` | 直接覆盖会丢掉本机对 skill 的临时修改 | 覆盖前自动备份到 `~/.local/state/agent-skills/backups/<时间戳>/`；已实测 |
| R8 | 信息 | 本机其余 100+ 个 `SKILL.md` | Codex 内置、插件市场缓存、NTD 市场、项目内嵌 | 不打包；清点与理由见 [INVENTORY.md](INVENTORY.md) |
| R9 | 低 | 5 个 `workflow-*` | 文案面向 Codex（"Use when Codex should…"），在 DSH/pi 上触发匹配略偏 | 保留：这组 skill 本来就是 Codex→pi 工作流，改文案会改变语义；要通用版应另开一套 |

## 二、逐 skill 结论

| Skill | 文件 | 外部依赖 | 结论 |
| --- | --- | --- | --- |
| `obsidian-notes` | 4 | `python3`（纯标准库）；Obsidian 可选 | 通过。helper 默认 vault 可覆盖，路径拒绝逃逸 |
| `minfadian` | 11 | `python3`（纯标准库）；仅重建时需要联网 | 通过。1260 条核对一致 |
| `ponytail-review` | 1 | 无 | 通过。纯提示词，短小 |
| `ruoyi-vue-pro-dev` | 8 | 无 | 通过。reference 齐全，引用路径全部存在 |
| `workflow-diagnose` | 2 | 无 | 通过 |
| `workflow-grill-with-docs` | 2 | 无 | 通过 |
| `workflow-implement` | 2 | 无 | 通过。引用的 `.pi/SYSTEM.md` 是目标项目文件，缺失时按"Read First"跳过即可 |
| `workflow-plan-acceptance` | 2 | 无 | 通过 |
| `workflow-review-md` | 2 | 无 | 通过 |
| `book-to-skill` | 上游仓库 | `python3` + 可选 PDF/EPUB/DOCX 解析器 | 通过（文本链 `pdftotext` 可用；`docling` 未装） |

## 三、验证记录

```text
$ python3 scripts/check-skills.py
9/9 个 skill 通过检查

frontmatter YAML 解析：9/9 成功（name 与目录一致，description 非空）
民法典条数：204+258+526+51+79+45+95+2 = 1260 ✓
敏感信息扫描：无 token / 私钥 / 服务器 IP
隔离 HOME 实装：agents + codex + pi 三目标 × 9 skill，全部落盘
外部安装：book-to-skill 按 526f362 克隆成功，.git 已剔除
重复安装：二次运行走 fetch+checkout，不重复克隆
软链模式：-l 生成指向仓库的 symlink，旧目录进备份
book-to-skill 自检：extract.py --check 可运行，文本 PDF 链 ready
```

## 四、未验证 / 已知限制

- **DSH 热重载未验证**：当前会话不能重启；但 `~/.agents/skills` 这个根已经被 DSH 加载过（`book-to-skill`、`minfadian` 就来自这里），路径本身是通的。
- **软链兼容性未逐个 agent 实测**：默认用复制，`-l` 作为进阶选项。
- **未在第二台真机跑过**：脚本在隔离 HOME（同机不同目录）验证，覆盖了克隆、备份、覆盖、软链、dry-run。
- **shellcheck 未跑**：本机没装；已用 `bash -n` 做语法检查。
- **book-to-skill 版本是旧的**：`526f362` 是这台机器上验证过的版本，上游已到 `a24e62f`；升级前建议先跑一次真实文档转换。

## 五、后续建议

1. 把 `AI-Project-Workflow-Template` 里未提交的 `workflow-review-md` 改动提交，减少快照与上游的漂移。
2. `book-to-skill` 每半年升一次 pin，升级后跑 `extract.py --check` + 一本真实 PDF。
3. 换 Obsidian vault 路径时不用改 skill，设 `OBSIDIAN_VAULT` 即可。
4. 新增 skill 先跑 `scripts/check-skills.py`，再 `./install.sh -o <name>`。

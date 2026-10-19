---
name: workflow-implement
description: Execute implementation work from the current .ai-workflow files in a project that uses the Codex to pi workflow. Use when the user wants the agent to start implementing without retyping the full workflow prompt.
---

# Workflow Implement

Use this skill to turn the current `.ai-workflow` state into implementation work.

## Read First

Read these files before making any code changes:

- `.ai-workflow/GOAL.md`
- `.ai-workflow/PLAN.md`
- `.ai-workflow/ACCEPTANCE.md`
- `.ai-workflow/REVIEW.md`
- `.pi/SYSTEM.md`

Treat `.ai-workflow` as current-task overwrite mode. These files describe the active task, not long-term task history.

## Companion Skills

- If implementation touches ruoyi-vue-pro, yudao-ui-admin-vue3, yudao-ui-admin-uniapp, or a ruoyi-based management backend, read and follow `ruoyi-vue-pro-dev` when installed. Use it for repository layout, backend conventions, frontend conventions, MySQL SQL, menus, permissions, and mock data; keep project architecture docs as the higher-level contract.
- Apply Ponytail-style simplicity during implementation: use repository-native patterns first, prefer the smallest sound solution, avoid speculative abstraction, and do not add dependencies or configuration surfaces without present-tense need.

## Working Rules

- Think before coding. Reconstruct the task background, change reason, scope, non-goals, acceptance target, and likely risk areas before editing.
- Implement the approved plan unless it is clearly blocked.
- Before editing, make sure you can restate the task background, the reason the change exists, the active scope, the non-goals, and the acceptance target.
- Simplicity first. Prefer the simplest sound solution that satisfies the task.
- Do not optimize for the smallest possible diff. Inside the approved scope, prefer sound design, robustness, maintainability, and reasonable extensibility.
- Reuse repository-native patterns before inventing new structure.
- Do not add speculative abstractions, generic extension points, or extra configuration surfaces without clear present-tense need.
- If the task touches backend code, preserve explicit layer ownership:
  - controllers are thin transport adapters
  - application services orchestrate use cases
  - repositories handle data access only
  - infrastructure owns persistence, external I/O, background jobs, and streaming
  - core/domain contracts stay free of infrastructure dependencies
- For backend work, do not:
  - put business workflows, broad `try/catch`, `DbContext`, or repository logic in controllers
  - put HTTP-specific response shaping, `ProblemDetails`, or `HttpContext` logic into services
  - leak entities, tracked persistence models, or SDK types across boundaries
  - collapse multiple concerns into one large file when the architecture already suggests a cleaner split
- For backend work, preserve DTO/domain/entity separation, explicit business exceptions, centralized middleware/filter handling, and traceability dimensions for requestId, traceId, actor, account, exchange, symbol, and outcome where relevant.
- Prefer simple, direct solutions over speculative abstractions.
- Fix blocking findings from `.ai-workflow/REVIEW.md` before considering the task complete.
- Avoid unrelated edits, but do not avoid necessary in-scope refactoring when it materially improves code quality.
- If the plan conflicts with the codebase, environment, tests, or runtime reality, stop and document the blocker in `.ai-workflow/IMPLEMENTATION_LOG.md` instead of silently redesigning the task.
- If the task is diagnosis-heavy or the failure mode is still unclear, prefer a diagnosis-first pass before broad fixes.
- Do not silently assume missing behavior. If required information is absent, record the assumption or blocker before continuing.
- For bug fixes, reproduce the failure with a test or concrete evidence first whenever feasible. If not feasible, explain why and add the strongest regression coverage you can.
- Run meaningful validation. Prefer targeted tests first, then broader validation as needed by the scope.
- Do not commit unless the user explicitly asks.

## Start Response

Before editing, briefly summarize in Chinese using exactly these top-level sections:

```md
## 工作流结果
- 技能: `workflow-implement`
- 状态: `in_progress`
- 产物: `IMPLEMENTATION_LOG.md`

## 实施摘要
- 当前目标: ...
- 修改背景: ...
- 修改原因: ...
- 本轮范围: ...
- 非目标: ...
- 后端分层路径: ...（如适用）
- Review 阻塞项: ...
- 首个动作: ...

## 下一步
- 开始实现并更新 `IMPLEMENTATION_LOG.md`
```

Then begin implementation.

## Required Log Update

When you finish a meaningful implementation pass, update `.ai-workflow/IMPLEMENTATION_LOG.md` with:

- status
- plan items addressed
- files changed
- key design decisions and why they were chosen
- validations run
- results
- deviations, blockers, or follow-up notes

Use this file shape:

```md
# Implementation Log

## Status
- `in_progress` | `blocked` | `ready_for_review` | `done`

## Goal Recap
- ...

## Background And Reason Consumed
- ...

## Plan Items Addressed
- ...

## Changes Made
- ...

## Key Design Decisions
- Decision:
  Why:

## Validation
- Command:
  Result:

## Deviations From Plan
- None / ...

## Blockers
- None / ...

## Next Suggested Review Focus
- ...
```

## Final response format

When stopping after an implementation pass, respond in Chinese with exactly these top-level sections:

```md
## 工作流结果
- 技能: `workflow-implement`
- 状态: `blocked` | `ready_for_review` | `done`
- 产物: `IMPLEMENTATION_LOG.md`

## 实施摘要
- 当前目标: ...
- 修改原因: ...
- 已完成: ...
- 验证: ...

## 下一步
- ...
```

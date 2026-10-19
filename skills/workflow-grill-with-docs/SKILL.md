---
name: workflow-grill-with-docs
description: Clarify a new feature, refactor, or ambiguous task against the existing codebase, docs, ADRs, and long-lived project context before planning. Use when Codex should align terminology, scope, architecture boundaries, and non-goals before creating `.ai-workflow` plans, especially for backend-heavy or structurally risky work.
---

# Workflow Grill With Docs

Align a task with the real repository before planning.

## Read First

Read the highest-signal context before proposing implementation:

- `AGENTS.md`
- `CONTEXT.md` if present
- `docs/README.md`
- relevant `docs/adr/*`
- relevant architecture or contract docs, especially backend implementation contracts when backend code is involved
- key existing code paths that the task will extend or modify

Do not assume the prompt already contains enough context. Rebuild context from the repository.

## Core Behavior

1. Clarify the user request against the current repository, not against an idealized design.
2. Build shared language before solutioning:
   - domain terms
   - architecture terms
   - current boundaries
   - explicit non-goals
3. Detect ambiguity, conflicting assumptions, and hidden scope expansion early.
4. Update or create `CONTEXT.md` as the durable long-lived context layer.
5. Hand off cleanly into `workflow-plan-acceptance`.

## Workflow

### 1. Reconstruct task context

Summarize:

- what the user wants
- what part of the system this touches
- whether the task is a feature, refactor, investigation, or cleanup
- whether the request appears to conflict with current architecture or docs

### 2. Read the repository language

Prefer repository-native terms over inventing new names.

Capture:

- current domain vocabulary
- current module and layer names
- existing request/response shapes
- existing architectural boundaries
- already-documented non-goals

### 3. Grill the task against reality

Resolve:

- hidden assumptions
- naming mismatches
- boundary violations implied by the request
- whether this belongs in controller, service, repository, infrastructure, orchestrator, background job, or docs only
- whether an ADR or durable docs update is likely required

Ask concise follow-up questions only if the ambiguity is material and cannot be resolved from local context. Otherwise make narrow assumptions and record them.

### 4. Update `CONTEXT.md`

Create `CONTEXT.md` if absent. Otherwise refresh only the sections affected by the task.

Use this shape:

```md
# Context

## Project Language
- Stable terms, role names, and abbreviations.

## Architecture Facts
- High-confidence facts about current structure and boundaries.

## Existing Patterns To Follow
- Reusable code, naming, layering, and workflow patterns already present.

## Active Boundaries And Non-Goals
- What this project or subsystem owns
- What it explicitly does not own

## Current Risks And Smells
- Known structural risks, backend smells, or areas of ongoing cleanup.

## Feature Or Task Notes
- Short task-specific notes that should survive into planning.

## Open Questions
- Unresolved items that may affect the next planning step.
```

`CONTEXT.md` is long-lived and cumulative. Do not overwrite unrelated project knowledge.

### 5. Hand off to planning

When the repository language and constraints are aligned, recommend `workflow-plan-acceptance`.

## Backend-specific rules

If backend code is involved, explicitly call out:

- the expected layer path, such as `controller -> application/service -> repository -> persistence/adapter`
- the current project-specific layer names
- thin-controller expectations
- service-centric orchestration expectations
- DTO / domain model / entity boundaries
- centralized exception, logging, metrics, and validation paths
- existing directory conventions that should not be broken

## Final response format

At the end, respond in Chinese with exactly these top-level sections:

```md
## 工作流结果
- 技能: `workflow-grill-with-docs`
- 状态: `completed`
- 产物: `CONTEXT.md`

## 对齐摘要
- 当前目标: ...
- 已确认上下文: ...
- 关键边界: ...
- 关键非目标: ...
- 未决问题: ...

## 下一步
- 使用 `workflow-plan-acceptance` 生成 `GOAL.md`、`PLAN.md`、`ACCEPTANCE.md`
```

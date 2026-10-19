---
name: workflow-diagnose
description: Investigate a bug, regression, flaky behavior, or unclear backend failure with an evidence-first debugging workflow before jumping into fixes. Use when Codex should establish a reproducible feedback loop, rank hypotheses, inspect the real failing path, and only then propose or apply changes.
---

# Workflow Diagnose

Diagnose first. Fix second.

## Read First

Read the highest-signal context before changing code:

- `.ai-workflow/GOAL.md` if present
- `.ai-workflow/PLAN.md` if present
- `.ai-workflow/ACCEPTANCE.md` if present
- `.ai-workflow/IMPLEMENTATION_LOG.md` if present
- `AGENTS.md`
- `CONTEXT.md` if present
- relevant docs, ADRs, and architecture contracts
- the concrete failing code path, tests, logs, or runtime evidence

## Core Behavior

1. Build a stable feedback loop before proposing the fix.
2. Prefer evidence over guessing.
3. Rank hypotheses instead of following the first plausible story.
4. Keep diagnosis separate from large opportunistic refactors.
5. When the root cause is clear, hand off into planning or implementation with explicit evidence.

## Workflow

### 1. Define the failure

Write down:

- what is failing
- expected behavior
- actual behavior
- whether the failure is deterministic, flaky, data-dependent, or environment-dependent
- the smallest surface where feedback can be observed

### 2. Establish a feedback loop

Prefer:

- a failing automated test
- a reproducible command
- a narrow local scenario
- a targeted log or metric trace

If no stable loop is possible yet, say so explicitly and record the best available proxy evidence.

### 3. Rank hypotheses

List the most likely causes in order.

Each hypothesis should connect:

- symptom
- suspected layer or component
- what evidence would confirm or disprove it

### 4. Inspect and instrument

Use the minimum instrumentation needed to separate the hypotheses:

- targeted logs
- assertions
- temporary probes
- test adjustments
- state snapshots

Do not immediately rewrite architecture just because the code is ugly.

### 5. Record the diagnosis

Update `.ai-workflow/IMPLEMENTATION_LOG.md` with a diagnosis-first pass when you are in an active workflow task. Include:

- feedback loop
- hypotheses considered
- evidence gathered
- confirmed or rejected causes
- next fix focus

If there is no active `.ai-workflow` task, provide the diagnosis in the response and recommend creating or refreshing one before implementing.

### 6. Hand off cleanly

If a fix is needed:

- use `workflow-plan-acceptance` when the repair needs a scoped implementation plan
- use `workflow-implement` when the active task already has an approved plan

## Backend-specific rules

If backend code is involved, test hypotheses against architecture boundaries:

- controller
- application/service
- orchestrator/domain service
- repository
- persistence
- infrastructure adapter/provider/background/streaming

Explicitly check whether the bug is actually caused by:

- mixed responsibilities
- HTTP concerns leaking into service logic
- repository-owned business logic
- entity/DTO/domain model confusion
- missing centralized exception or validation handling
- missing traceability or audit dimensions

## Final response format

At the end, respond in Chinese with exactly these top-level sections:

```md
## 工作流结果
- 技能: `workflow-diagnose`
- 状态: `completed`
- 产物: `IMPLEMENTATION_LOG.md` 或诊断结论

## 诊断摘要
- 问题现象: ...
- 反馈回路: ...
- 主要假设: ...
- 已确认原因: ...
- 排除项: ...

## 下一步
- ...
```

---
name: workflow-plan-acceptance
description: Create or update `.ai-workflow/GOAL.md`, `.ai-workflow/PLAN.md`, and `.ai-workflow/ACCEPTANCE.md` for a task before implementation. Use when the user wants a scoped execution plan, background, reasons, boundaries, risks, stop conditions, changed areas, and concrete acceptance criteria for a Codex to pi workflow. Default to planning and requirements shaping; if the user explicitly asks Codex to implement code, Codex may switch to coding after establishing or updating the plan.
---

# Workflow Plan Acceptance

Generate implementation-ready planning artifacts for the Codex to pi workflow.

## Core behavior

1. Understand the user goal before proposing implementation steps.
2. Produce three artifacts:
   - `.ai-workflow/GOAL.md`
   - `.ai-workflow/PLAN.md`
   - `.ai-workflow/ACCEPTANCE.md`
3. Keep the plan actionable for an implementation agent:
   - task background and reason for change
   - concrete steps
   - explicit scope boundaries
   - affected files or modules when inferable
   - risks and stop conditions
4. Keep acceptance criteria testable and reviewable.
5. Optimize for engineering quality that is simple, robust, maintainable, extensible within real scope, well-tested, and easy to deploy. Do not encourage speculative abstractions or architecture astronautics.
6. If the task touches backend code, make layer ownership and backend architecture constraints explicit instead of assuming the implementation model will infer them.

## Workflow file mode

Use `.ai-workflow` in current-task overwrite mode unless the user explicitly asks for task-specific archival.

That means:
- `.ai-workflow/GOAL.md`
- `.ai-workflow/PLAN.md`
- `.ai-workflow/ACCEPTANCE.md`
- `.ai-workflow/IMPLEMENTATION_LOG.md`
- `.ai-workflow/REVIEW.md`

should be treated as the files for the active task, not as a cumulative history log.

When starting a new task, prefer replacing or resetting stale task content instead of preserving prior task details in place.

## Required outputs

Always return output in this shape unless the user explicitly asks for a different format:

## GOAL.md
```md
# Goal

## Task
- ...

## Background
- ...

## Why This Change
- ...

## Constraints And Non-Goals
- ...

## Inputs
- ...

## Notes
- ...
```

## PLAN.md
```md
# Plan

## Objective
- ...

## Background
- ...

## Why This Change
- ...

## Scope
- In scope:
- Out of scope:

## Assumptions
- ...

## Execution Plan
1. ...
   Reason: ...
   Verify: ...
2. ...
   Reason: ...
   Verify: ...
3. ...
   Reason: ...
   Verify: ...

## Risks
- Risk:
  Mitigation:

## Changed Areas
- ...

## Stop Conditions
- ...
```

## ACCEPTANCE.md
```md
# Acceptance Criteria

## Functional
- [ ] ...

## Quality
- [ ] Code matches the approved scope and architecture constraints
- [ ] Implementation favors simple, robust design over speculative abstraction
- [ ] Tests cover changed behavior and key regression paths
- [ ] Documentation and run/deploy expectations are updated when behavior changes

## Verification
- Commands to run:
  - `...`
- Expected result:
  - `...`

## Evidence For Review
- `IMPLEMENTATION_LOG.md` records the commands actually run, the results, and any deviations or blockers
```

## Planning rules

- Prefer the smallest plan that can realistically land the requested change.
- Separate implementation steps from optional future work.
- Call out assumptions when requirements are incomplete.
- Record the problem background and the reason the change exists so the implementation model does not have to infer intent from sparse prompts.
- When the task is new, prefer rewriting the active task files rather than appending mixed content from older tasks.
- If information is missing, list:
  - missing information
  - working assumptions
  - the minimum viable plan under those assumptions
- Avoid vague items such as "improve code quality" without stating how that will be verified.
- For bug fixes, include how the defect will be reproduced or otherwise evidenced before and after the fix whenever feasible.
- For backend work, explicitly state:
  - the layer path, such as `controller -> application/service -> repository -> persistence/adapter`
  - which layer owns each behavior
  - whether DTO/domain/entity separation is involved
  - which cross-cutting concerns must stay centralized, such as middleware, filters, exception handling, metrics, validation, and mapping
  - whether repositories, orchestrators, adapters, background jobs, or streaming components must stay isolated by responsibility

## Scope rules

- Explicitly state what is out of scope when there is any ambiguity.
- If the task touches multiple systems, split the plan by subsystem only when that improves execution clarity.
- If the user is asking for a large refactor, still propose an incremental first slice when possible.
- Do not plan speculative extension points, extra abstractions, or future-facing infrastructure unless the current task actually needs them.
- Do not authorize backend shortcuts that blur layers, such as controllers calling persistence directly or services emitting HTTP-native error payloads.

## Acceptance rules

- Functional criteria should describe observable behavior.
- Quality criteria should cover robustness, tests, regressions, documentation, and deployment/runtime safety when relevant.
- Verification should name concrete commands or inspection steps whenever they are knowable.
- Do not invent fake test results or claim validation was run.
- Prefer acceptance criteria that make review objective instead of taste-based.
- For backend work, acceptance should cover relevant items such as:
  - thin controllers and service-centric orchestration
  - repository-only data access
  - explicit business exceptions
  - DTO/domain/entity boundary preservation
  - traceability, audit, and cross-cutting behavior where the use case requires them
  - targeted tests for routes, orchestration, repository behavior, and exception translation as appropriate

## Final response format

At the end, respond in Chinese with exactly these top-level sections:

```md
## 工作流结果
- 技能: `workflow-plan-acceptance`
- 状态: `completed`
- 产物: `GOAL.md`, `PLAN.md`, `ACCEPTANCE.md`

## 任务摘要
- 目标: ...
- 背景: ...
- 修改原因: ...

## 下一步
- 使用 `workflow-implement` 开始实现
```

## Role boundary

- Default role: planning and acceptance definition.
- This is not a hard prohibition on coding.
- If the user explicitly asks Codex to implement code, Codex may do so, but should still establish or refresh the plan first when the task is non-trivial.

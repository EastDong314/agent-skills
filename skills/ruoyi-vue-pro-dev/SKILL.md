---
name: ruoyi-vue-pro-dev
description: 'Develop against ruoyi-vue-pro/Yudao projects, including backend modules, Vue3 admin UI, uni-app UI, SQL, permissions, and data-integration boundaries.'
---

# ruoyi-vue-pro Dev

Use this skill for ruoyi-vue-pro / Yudao-based development. Follow the actual repository branch first; these notes only fill in the conventions agents commonly miss.

## Quick workflow

1. Clarify module, admin/app端, page entry, permissions, tenant/data-scope needs, dictionaries, import/export, audit/logging, and which branch/JDK the project has selected.
2. Inspect nearby implemented modules before editing. Reuse existing Controller, Service, Mapper, VO, API, page, and SQL patterns.
3. Design the data model, API contract, permission strings, menus, and dictionaries before implementation. Keep SQL aligned with backend annotations and frontend permission checks.
4. Read only the references needed for the task:
   - Repo structure and branch checks: `references/repo-map.md`
   - Backend conventions: `references/backend-conventions.md`
   - Vue3 admin frontend: `references/frontend-vue3-conventions.md`
   - uni-app frontend: `references/frontend-uniapp-conventions.md`
   - MySQL SQL, menus, permissions, dictionaries: `references/db-mysql-conventions.md`
   - Redis / analytics DB / external system boundaries: `references/integration-boundaries.md`
   - Mock or seed data: `references/mock-data.md`
5. Validate with the smallest relevant checks: compile/test the touched backend module, type-check/lint the touched frontend package, and review generated SQL for permissions and encoding.

## Global rules

- Keep files UTF-8. Prefer LF line endings for skill/reference files and new project files.
- Any database change must be expressed as SQL (schema and data).
- Frontends call backend APIs only. Do not let browser, app, or large-screen pages connect directly to databases, Redis, or message brokers.
- Do not add new dependencies until existing ruoyi/Yudao modules, framework helpers, or platform features are insufficient.
- Ask targeted questions only when module, entry, permission, data ownership, or reporting semantics cannot be inferred safely.

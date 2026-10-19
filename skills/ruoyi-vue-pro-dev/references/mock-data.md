# Mock Data Guidelines

When asked to generate mock SQL, prioritize realistic, relationally-consistent data and sufficient volume.

## Process

1. Read schema from `sql/mysql/ruoyi-vue-pro.sql`.
2. Identify core entities and relationships (FK-like fields, tenant_id, status, dict types).
3. Build data in dependency order (dicts/org/users -> business tables -> logs).
4. Generate inserts in batches and wrap with `BEGIN; ... COMMIT;`.

## Data quality rules

- Respect unique constraints and code/name uniqueness.
- Use realistic Chinese names, phones, emails, addresses; timestamps within recent months.
- Populate status fields with valid dict values.
- Ensure `tenant_id` is consistent per tenant; create 2–3 tenants if multi-tenant data exists.
- For list pages, create enough rows to test pagination and filters (50–200+ rows per core table).

## Insert style

- Keep consistent field order with table definition.
- For nullable fields, use NULL rather than empty string when appropriate.
- Keep comments/labels readable (UTF-8).

## Example snippet

```
BEGIN;
INSERT INTO `module_xxx` (`id`, `name`, `status`, `create_time`, `update_time`, `creator`, `updater`, `deleted`, `tenant_id`)
VALUES
(1, '示例A', 0, '2025-11-01 10:00:00', '2025-11-01 10:00:00', 'admin', 'admin', b'0', 1),
(2, '示例B', 1, '2025-11-02 10:00:00', '2025-11-02 10:00:00', 'admin', 'admin', b'0', 1);
COMMIT;
```

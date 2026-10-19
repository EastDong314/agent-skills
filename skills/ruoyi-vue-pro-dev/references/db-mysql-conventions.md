# DB & SQL Conventions (MySQL)

Database changes must be expressed as SQL scripts.

## Schema location

- Base schema: `sql/mysql/ruoyi-vue-pro.sql`
- Quartz schema: `sql/mysql/quartz.sql`
- For existing deployments, provide migration SQL separately when the project already has an established migration process. Do not rely on dropping existing tables.

## Naming & columns

- Table naming: module prefix + business name, e.g. `system_users`, `infra_api_access_log`, `bpm_task`.
- Common columns for business tables:
  - `id` bigint PK
  - `create_time`, `update_time`
  - `creator`, `updater`
  - `deleted` (logical delete)
  - `tenant_id` (if tenant data)
- Always use `utf8mb4` and add `COMMENT` on table/columns.

## Add a table (pattern)

```
-- ----------------------------
-- Table structure for module_xxx
-- ----------------------------
DROP TABLE IF EXISTS `module_xxx`;
CREATE TABLE `module_xxx` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  ...
  `tenant_id` bigint NOT NULL DEFAULT 0 COMMENT '租户编号',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='XXX表';

-- ----------------------------
-- Records of module_xxx
-- ----------------------------
BEGIN;
COMMIT;
```

For migration scripts, prefer explicit `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE`, and idempotent `INSERT`/`UPDATE` patterns when the deployment process supports them.

## Menu & permission data

- Menus and permissions are in `system_menu` with `type`:
  - 1 目录, 2 菜单, 3 按钮
- Permission strings must align across:
  - Backend: `@PreAuthorize("@ss.hasPermission('module:xxx:action')")`
  - Frontend: `v-hasPermi="['module:xxx:action']"`
  - DB: `system_menu.permission`
- New pages require `system_menu` inserts for menu + buttons.
- Keep route component paths aligned with the actual frontend repo layout.

## Dicts

- Add dict types in `system_dict_type` and entries in `system_dict_data`.
- Keep code constants in `DictTypeConstants` / frontend `DICT_TYPE` aligned.

## Multi-tenant data

- Tenant-owned business tables normally include `tenant_id` and DOs extend `TenantBaseDO`.
- Global dictionaries/configuration tables may be non-tenant or use `@TenantIgnore`; match the corresponding existing module.
- Do not add `tenant_id` to analytical/time-series tables blindly. Decide based on query isolation, retention, and ingestion path, then document the decision in SQL comments or project docs.

## Encoding

- Keep SQL files in UTF-8 (prefer `SET NAMES utf8mb4;`).
- Avoid garbled Chinese text in comments/labels.

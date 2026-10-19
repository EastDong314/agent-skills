# Repo Map

## Backend

- Root: `ruoyi-vue-pro` or the project fork based on it.
- Check the selected branch before coding. Some projects use JDK-specific branches such as `master-jdk25`; verify `java.version`, Spring Boot version, and module list from the local `pom.xml`.
- Modules:
  - `yudao-module-system`
  - `yudao-module-infra`
  - Common optional modules: `yudao-module-bpm`, `yudao-module-crm`, `yudao-module-erp`,
    `yudao-module-mall`, `yudao-module-member`, `yudao-module-pay`, `yudao-module-report`,
    `yudao-module-mp`, `yudao-module-iot`, `yudao-module-ai`, `yudao-module-mes`,
    `yudao-module-wms`, `yudao-module-hrm`, `yudao-module-fms`, `yudao-module-pms`,
    `yudao-module-im`.
- Framework: `yudao-framework` (common utilities, web, mybatis, tenant, data-permission, security)
- App bootstrap: `yudao-server`
- SQL: usually `sql/mysql/ruoyi-vue-pro.sql`, `sql/mysql/quartz.sql`; some branches include other database dialects.
- `yudao-server/pom.xml` often enables only system/infra by default. Add required module dependencies deliberately.

## Frontend (separate repos)

- Vue3 + Element Plus: `yudao-ui-admin-vue3`
- Vben (Ant Design Vue): `yudao-ui-admin-vben`
- Vue2 + Element UI: `yudao-ui-admin-vue2`
- uni-app admin/app: `yudao-ui-admin-uniapp`
- GoView large-screen designer integration usually lives under report-related repos/modules.

Use Vue3 + Element Plus by default unless the user specifies otherwise.

# Frontend Conventions (Vue3 + Element Plus)

Use `yudao-ui-admin-vue3` as the reference. Keep UI consistent with existing pages.

## Structure

- API layer: `src/api/<module>/.../*.ts`
- Pages: `src/views/<module>/.../*.vue`
- Shared UI: `src/components`, `src/layout`, `src/styles`
- Utils/hooks: `src/utils`, `src/hooks`
- Use the package manager declared by the repo lockfile/package metadata, commonly `pnpm`.

## API conventions

- Use `request` wrapper from `@/config/axios`.
- Naming commonly follows `getXxxPage`, `getXxx`, `createXxx`, `updateXxx`, `deleteXxx`, `exportXxx`. Some modules export an `XxxApi` object; match nearby files.
- `PageParam` comes from `types/global.d.ts`.
- API methods should call backend paths only, never Redis/database/broker endpoints directly.

Example:

```ts
import request from '@/config/axios'

export interface XxxVO {
  id: number
  name: string
  status: number
}

export const getXxxPage = (params: PageParam) =>
  request.get({ url: '/module/xxx/page', params })

export const getXxx = (id: number) =>
  request.get({ url: '/module/xxx/get?id=' + id })

export const createXxx = (data: XxxVO) =>
  request.post({ url: '/module/xxx/create', data })
```

## Component conventions

- Use `<script setup lang="ts">`.
- Set component name: `defineOptions({ name: 'ModuleXxx' })`.
- Use `ContentWrap`, `Pagination`, `Dialog` for consistent layout.
- Use `useMessage()` for success/error prompts; use `useI18n()` for text.
- Apply permission control with `v-hasPermi` or `checkPermi([...])`.
- Use `DICT_TYPE` + `getIntDictOptions` for dict selects.

## Form validation

- Use `FormRules` + `el-form` with `rules`.
- `formRef.value.validate()` before submit.
- Match backend validation rules where possible.

## Error handling

- Rely on Axios interceptors in `src/config/axios/service.ts`.
- For manual errors, call `message.error(...)` or `ElNotification.error(...)`.

## UI consistency

- Keep button types aligned with existing pages:
  - primary (新增/保存), warning (导入), success (导出), danger (删除).
- Use `Icon` component consistently.
- Avoid custom colors; use Element Plus theme and existing utility classes.
- For operational/admin pages, prefer dense, scannable tables and dialogs. Use richer cards/charts only when the existing module already does.
- Keep long-running report or chart pages bounded: fixed refresh intervals, cancel stale requests, and cap returned data points through backend parameters.

## Template snippets

### List page skeleton

```vue
<template>
  <ContentWrap>
    <el-form :model="queryParams" ref="queryFormRef" :inline="true">
      <!-- fields -->
      <el-form-item>
        <el-button @click="handleQuery"><Icon icon="ep:search" />搜索</el-button>
        <el-button @click="resetQuery"><Icon icon="ep:refresh" />重置</el-button>
        <el-button type="primary" plain @click="openForm('create')" v-hasPermi="['module:xxx:create']">
          <Icon icon="ep:plus" />新增
        </el-button>
      </el-form-item>
    </el-form>
  </ContentWrap>
  <ContentWrap>
    <el-table :data="list" v-loading="loading">
      <!-- columns -->
    </el-table>
    <Pagination :total="total" v-model:page="queryParams.pageNo" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </ContentWrap>
  <XxxForm ref="formRef" @success="getList" />
</template>
<script setup lang="ts">
import * as XxxApi from '@/api/module/xxx'
const message = useMessage()
const list = ref([])
const queryParams = reactive({ pageNo: 1, pageSize: 10 })
</script>
```

### Form dialog skeleton

```vue
<Dialog v-model="dialogVisible" :title="dialogTitle">
  <el-form ref="formRef" :model="formData" :rules="formRules">
    <!-- fields -->
  </el-form>
  <template #footer>
    <el-button type="primary" @click="submitForm">确 定</el-button>
    <el-button @click="dialogVisible = false">取 消</el-button>
  </template>
</Dialog>
```

# Frontend Conventions (uni-app)

Use `yudao-ui-admin-uniapp` or the project fork as the reference when building mobile/app/H5 views.

## Structure

- API layer: `src/api/<module>/.../*.ts`
- HTTP wrapper: `src/http/http.ts` and interceptors in `src/http/interceptor.ts`
- Pages and subpackages: follow `pages.config.ts` and nearby `src/pages-*` modules.
- App manifest: prefer `manifest.config.ts`; do not hand-edit generated files unless the repo documents that path.

## API and auth

- Use the project `http` wrapper. It handles base URL, token refresh, tenant headers, encryption flags, and platform URL behavior.
- Keep API function names and types close to the Vue3 admin API when both clients call the same backend.
- Frontend clients call backend APIs only. Do not connect mobile code directly to Redis, databases, MQTT brokers, or analytics engines.

## Platform checks

- Android support is usually through `app` / `app-android` scripts; verify scripts in `package.json`.
- Harmony support may be present through `@dcloudio/uni-app-harmony` or `@dcloudio/uni-mp-harmony`; verify the current repo scripts, DCloud/HBuilderX requirements, native plugins, and target device policy before promising delivery.
- App-side Pinia stores should be called inside functions/hooks when the repo documents that top-level calls cause app white-screen issues.

## UI

- Reuse existing components, tabbar/router patterns, UnoCSS utilities, and module layouts.
- Mobile screens should optimize first for field work: readable status, obvious refresh state, large tap targets, and offline/error feedback.
- For charts, test on the real target platform or simulator. Canvas and text measurement behavior may differ across H5, Android, and Harmony.

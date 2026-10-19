# Integration Boundaries

Use this reference when a ruoyi/Yudao project connects to Redis, message brokers, analytics databases, time-series databases, large-screen dashboards, or external systems.

## Ownership

- MySQL is the default source for management data: users, roles, menus, dictionaries, device/master data, and business configuration.
- Redis is for cache, token/session helpers, locks, short-lived state, idempotency keys, online status, and realtime snapshots when the project chooses that pattern.
- Analytics or time-series databases are for high-volume historical facts and aggregates. Treat them as separate stores with explicit query limits and retention rules.
- Message brokers move events between services. Management frontends should not publish directly to brokers unless the project has an explicit, reviewed reason.

## Backend access

- Put integration code behind backend services. Vue, uni-app, and GoView pages should call backend APIs only.
- Prefer existing framework starters and helpers before adding drivers or clients.
- When adding another datasource, define clear read/write ownership, transaction expectations, health checks, credentials, and timeout settings.
- For report endpoints over large data, require time range limits, page limits, point-count limits, and defensive defaults.

## Large-screen and report data

- Large-screen dashboards may use GoView or custom pages, but data should still flow through backend-controlled APIs or reviewed datasource configuration.
- Avoid arbitrary SQL execution for untrusted users. If SQL-backed dashboards are enabled, restrict datasource permissions and query scope.
- Start with detail-table queries only for small PoC data. Add minute/hour/day aggregates when refresh frequency, time range, or data volume makes detail scans slow.

## Operations

- Document retention, cleanup, backup, and restore behavior for every non-MySQL data store.
- Scripts intended for operators should use clear Chinese prompts and avoid unexplained abbreviations when the surrounding project uses Chinese operations workflows.

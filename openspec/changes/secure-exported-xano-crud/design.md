# Design

Retain FastAPI login and persistent student binding. Xano CRUD is an internal service protected by X-API-Key against XANO_API_KEY. This is not native end-user authorization on Xano. The server credential must never be issued to browser clients. A later design decision is required to satisfy literal auth.id checks on Xano.

The deployment tree excludes API-group files containing Swagger tokens, environment exports, records and unrelated workspace primitives. Stable existing GUIDs identify the fifteen routes and validation function. Table schemas are preserved separately as reference files. PATCH picks explicit mutable keys present in the raw request; removing filter_null/filter_empty_text permits clearing nullable deadlines and text. Xano validation and dry-run remain required before applying.

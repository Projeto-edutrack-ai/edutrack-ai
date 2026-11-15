# Change: add-xano-user-ownership-activity13

## Why

The existing Xano CRUD routes use a shared server credential and do not establish native per-user identity in Xano. This change plans a separate private Xano API group for `materias`, while preserving the current login, frontend, FastAPI integration, and authorization boundary.

## What Changes

- Add an optional, unique `alunos.user_id` reference to Xano `user`; leave existing unlinked records unchanged.
- Define an explicit administrative linking process after verifying both identities; never link by email or assumed ID equality.
- Add a separate private Xano API group for `materias` CRUD using `auth = "user"` and ownership through `materias.alunos_id` → `alunos.user_id` → `$auth.id`.
- Expose list/create at `GET` and `POST /privado/materias`, and read/update/delete at `GET`, `PATCH`, and `DELETE /privado/materias/{materias_id}`.
- Test the new APIs with two team-controlled Xano test accounts using native Xano login; keep credentials and tokens out of the repository.
- Keep existing server-key routes unchanged. Their per-user authorization continues to depend on FastAPI; this change does not claim that existing CRUD has been migrated.

## Capabilities

### New Capabilities
- `xano-user-ownership`: optional verified student-to-user association and user-scoped CRUD in a separate private Xano API group for subjects.

### Modified Capabilities
- None.

## Impact

Xano `alunos.user_id` and a new private API group for subject listing, creation, reading, updating, and deletion. No changes to application login, frontend, FastAPI integration, or existing server-key routes are in scope.

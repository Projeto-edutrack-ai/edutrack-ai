# Design

## Context

See [proposal.md](./proposal.md) for motivation. Existing application requests continue through the current login, frontend, and FastAPI integration. Existing Xano routes protected by a server key still rely on FastAPI for individual authorization. This change adds a separate Xano-native private API group and does not migrate those routes.

## Goals / Non-Goals

**Goals:**
- Provide user-scoped Xano CRUD for `materias` in a separate API group.
- Preserve unlinked student records and the current application behavior.
- Verify the new CRUD using native Xano tokens for two controlled test accounts without storing credentials in the repository.

**Non-Goals:**
- Add dual-token handling to the app or change login, frontend, or FastAPI integration.
- Migrate existing server-key CRUD routes or claim they enforce Xano-native user ownership.
- Link records automatically or modify existing academic data in bulk.

## Decisions

### Keep the association optional and unique

Add nullable `alunos.user_id` referencing Xano `user.id`, with uniqueness so one Xano user can be linked to at most one student. Leave the field null for existing unlinked records. An administrator explicitly links a student only after verifying control of both identities. Email matches and equal-looking IDs are not proof.

### Add a separate native-user API group

Create a distinct private Xano API group for `materias` with `auth = "user"`. Every operation derives ownership from `materias.alunos_id` → `alunos.user_id` → `$auth.id`. Listing is restricted to the authenticated user's student. Reading, updating, and deleting a record owned by another user are denied without exposing or changing it.

The group exposes `GET /privado/materias` and `POST /privado/materias`. For an individual subject, it exposes `GET /privado/materias/{materias_id}`, `PATCH /privado/materias/{materias_id}`, and `DELETE /privado/materias/{materias_id}`.

For creation, resolve the student from `$auth.id` and set `materias.alunos_id` on the server. Do not trust a client-supplied owner ID; reject creation if the authenticated user has no linked student. Do not permit updates to transfer ownership by changing `alunos_id`.

### Keep current application and routes unchanged

The new API group is not integrated into the existing app in this change. Current server-key routes remain as they are, and their per-user authorization continues to be enforced by FastAPI. This is a separate Xano-native CRUD surface, not a claim that all existing CRUD has moved to native user auth.

### Use two controlled accounts for native-login tests

Obtain test tokens by logging in through Xano's native user login with two team-controlled test accounts. The owner account has an administratively verified student link. Test the second account while it is unlinked, then explicitly link it to a different test student and test cross-owner isolation in both directions. Test unauthenticated calls without a token. Supply test credentials through a secure runtime mechanism, never source files, fixtures committed to the repository, logs, or test output.

## Risks / Trade-offs

- **[Legacy routes may be mistaken for migrated routes]** → Keep the route groups separate and document that existing server-key routes still rely on FastAPI for individual authorization.
- **[Incorrect administrative association]** → Require proof of both identities, audit the administrative action, and enforce uniqueness; never use email or ID equality.
- **[Unlinked records are inaccessible through the new group]** → Preserve them unchanged and deny access until an explicit verified link exists.
- **[Test credentials or tokens leak]** → Inject secrets only at runtime, redact outputs, and verify none are committed.

## Migration Plan

No application or existing-route migration is planned. Add the optional field without backfilling, administratively link only explicitly verified test/eligible records, deploy the separate private API group, and verify it with the controlled accounts. Rollback disables the new group or its tests; it does not delete records, clear links, or change existing routes.

## Reported Manual Execution Evidence

The following results were manually reported by the student and were not independently reproduced during this documentation update. No Xano calls were made as part of this update.

### Workspace push and association field

- Xano accepted a push of seven documents to workspace `147367`; the new private routes were called after the push.
- `alunos.user_id` was created, and existing records remained `null`.
- These results establish the reported push outcome for workspace `147367` only. They do not establish that the workspace is isolated or non-production.

### Account and CRUD observations

- Native registration of accounts A and B succeeded, and native login for account B succeeded.
- An unauthenticated browser request to `GET /privado/materias` returned `ERROR_CODE_UNAUTHORIZED`.
- An authenticated request by account A while it had no linked student returned `ERROR_CODE_ACCESS_DENIED`; the specific operation was not recorded.
- The test links were user `2` → student `8` and user `3` → student `9`.
- Account A's initial list was empty. It created subject `24` with `alunos_id = 8`, then read and patched it successfully.
- Account B created subject `25` with `alunos_id = 9`; its list returned only subject `25`.
- Account B's `GET`, `PATCH`, and `DELETE` attempts against subject `24` each returned `ERROR_CODE_NOT_FOUND`.
- Account A subsequently confirmed subject `24` still had its name and workload unchanged, deleted it, and received `ERROR_CODE_NOT_FOUND` on a later GET.
- Subject `25` remains in the Xano workspace as a test record.
- The final tests for account A used an internal token generated by the Xano panel. Those calls are not evidence of a new native-login test for account A.

This evidence applies only to the new `edutrack privado` group. It does not validate or migrate the existing server-key routes used by the application, whose individual authorization continues to depend on FastAPI.

### Remaining verification

The uniqueness behavior of `alunos.user_id` has not been verified, including whether multiple `null` values are permitted and whether duplicate non-null user references are rejected. The isolation status of workspace `147367`, native login for account A, the exact operation denied for unlinked account A, and account B's own read, update, and delete operations were not established by the reported results.

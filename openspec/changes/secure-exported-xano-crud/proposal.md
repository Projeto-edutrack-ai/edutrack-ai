# Change: Secure exported Xano CRUD

## Why
The real export confirms fifteen unprotected academic endpoints. Preserve Portuguese names, native GUIDs and legacy objects while preparing a server-only guard.

## What Changes
- Add the existing auth/validate_api_key function call before every academic operation.
- Restrict PATCH to documented mutable fields, including explicit null deadlines and empty descriptions.
- Store a sanitized, limited deployment directory and audit instructions.
- Match simulated DELETE response to the real null response.

## Impact
Only the academic endpoints and the already existing validation function are packaged for deployment. No database migration, credential export or remote push occurs. Native per-user Xano authentication and Xano search/report orchestration remain pending.

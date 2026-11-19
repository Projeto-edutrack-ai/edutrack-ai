## 1. Local preparation
- [x] Inspect actual schemas, relationships and CRUD code.
- [x] Prepare fifteen guarded endpoints with preserved GUIDs.
- [x] Restrict PATCH keys and preserve explicit nullable updates.
- [x] Include existing guard function without environment values.
- [x] Document real findings and rollout.
- [x] Run local regression checks: 61 Python tests, 7 JavaScript tests; OpenSpec strict validation passed.

## 2. Workspace verification
- [x] Configure XANO_API_KEY privately in Xano and matching backend header.
- [x] Run Xano push dry-run and inspect parsed remote diff.
- [x] Deploy only reviewed academic files.
- [ ] Test unauthorized access, CRUD and explicit null updates on real workspace.
- [ ] Complete Xano search/PDF endpoints and native user isolation assessment.

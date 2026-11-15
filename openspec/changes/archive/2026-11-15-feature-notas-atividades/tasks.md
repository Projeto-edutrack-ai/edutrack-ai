# Tasks

## 1. Resolve implementation prerequisites

- [ ] 1.1 Define a verifiable teacher identity and the persistent authorization relationship to the exact student and activity; verify completion by updating the design/spec with reviewed allowed and denied authorization scenarios, without treating `subjects.professor` as identity.
- [ ] 1.2 Select the authoritative grade store and define persistent student/activity ID mapping; verify completion by documenting the selected source of truth and tests/fixtures that reject unlinked or mismatched IDs.
- [ ] 1.3 Define the grade representation, precision, limits, and correction/history behavior; verify completion by updating the grade contract with boundary and resubmission scenarios.

## 2. Implement protected grade storage and submission

- [ ] 2.1 Add grade persistence and an additive migration using the approved store and relationship rules; verify migration tests preserve existing academic records and enforce the approved student-activity association.
- [ ] 2.2 Implement backend authorization for the verified teacher identity and exact student/activity relationship; verify tests allow an authorized teacher and reject unknown, unauthorized, or mismatched principals without writing a grade.
- [ ] 2.3 Implement grade submission and validation using the approved representation and correction policy; verify tests cover valid values, boundary values, persistence, and resubmission behavior.
- [ ] 2.4 Add the teacher-facing submission flow through the authenticated backend contract; verify frontend tests confirm the submitted student/activity context and never perform direct data-store writes.
- [ ] 2.5 Document the approved grade submission and authorization contract; verify documented behavior matches the delta spec and the implementation tests.

## 3. Verify end-to-end behavior

- [ ] 3.1 Run focused backend, frontend, and OpenSpec validation for the completed feature; verify an authorized submission persists against the intended student/activity and every denied submission leaves stored grades unchanged.

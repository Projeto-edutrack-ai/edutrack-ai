# Spec Delta

## Purpose

This capability defines optional verified ownership links and native per-user subject CRUD in a separate private Xano API group, without changing the existing application integration.

## ADDED Requirements

### Requirement: Optional verified student-to-user association
The system SHALL allow an administrator to link an Xano student to at most one Xano user after explicitly verifying both identities, while preserving students without a link.

#### Scenario: Existing student remains unlinked
- **WHEN** an existing student has no verified user association
- **THEN** the system preserves the record and leaves `alunos.user_id` unset

#### Scenario: Administrator links verified identities
- **WHEN** an administrator explicitly links a student and a Xano user after verifying control of both identities
- **THEN** the system records the optional association and prevents another student from being linked to the same user

#### Scenario: Link is based only on matching identifiers
- **WHEN** an association is proposed solely because email addresses or ID values match
- **THEN** the system does not create the association

### Requirement: Private subject CRUD is scoped to the authenticated Xano user
The system SHALL expose subject list and create at `GET /privado/materias` and `POST /privado/materias`, and read, update, and delete at `GET`, `PATCH`, and `DELETE /privado/materias/{materias_id}` in a separate private API group authenticated with `auth = "user"`. It SHALL authorize ownership through `materias.alunos_id` → `alunos.user_id` → `$auth.id`.

#### Scenario: Owner lists subjects
- **WHEN** a linked user lists subjects in the private API group
- **THEN** the API returns only subjects owned through that user's association

#### Scenario: Owner reads a subject
- **WHEN** a linked user reads a subject owned through the ownership chain
- **THEN** the API returns that subject

#### Scenario: Another owner reads a subject
- **WHEN** a different linked user attempts to read a subject owned by someone else
- **THEN** the API denies the operation without disclosing the subject

#### Scenario: Owner creates a subject
- **WHEN** a linked user creates a subject in the private API group
- **THEN** the API resolves the student from `$auth.id` and assigns that student's ID to `materias.alunos_id`, regardless of a client-supplied owner ID

#### Scenario: User without a linked student creates a subject
- **WHEN** an authenticated user without a linked student attempts to create a subject
- **THEN** the API denies creation and does not create an unowned or reassigned subject

#### Scenario: Another owner updates or deletes a subject
- **WHEN** a different linked user attempts to update or delete a subject they do not own
- **THEN** the API denies the operation without changing or deleting the subject

#### Scenario: Owner updates or deletes a subject
- **WHEN** the linked owner updates or deletes their subject
- **THEN** the API performs the requested operation without allowing ownership transfer through an update

#### Scenario: Unlinked user accesses an existing subject
- **WHEN** an authenticated user without a linked student attempts to read, update, or delete an existing subject
- **THEN** the API denies the operation without disclosing or changing the subject

#### Scenario: Unauthenticated caller accesses subject CRUD
- **WHEN** a caller invokes any private subject CRUD operation without a valid Xano user token
- **THEN** the API denies the request

### Requirement: Existing service-key routes retain their current authorization boundary
The system SHALL keep existing server-key routes separate from the new private subject API group, and SHALL NOT claim that this change migrates existing CRUD to native Xano user authorization.

#### Scenario: Existing application continues using current routes
- **WHEN** the existing application uses a current server-key route
- **THEN** its per-user authorization continues to depend on FastAPI and the route is not represented as migrated by this change

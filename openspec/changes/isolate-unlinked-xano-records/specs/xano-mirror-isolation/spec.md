# Xano Mirror Isolation Specification

## Purpose
Impedir que registros não associados bloqueiem o espelho de outra conta sem descartar dados próprios.

## ADDED Requirements

### Requirement: Scope ownership validation
The system SHALL ignore unlinked records not previously mirrored for the current user and SHALL NOT import or reassign them.

#### Scenario: Unrelated legacy subject lacks an owner
- **WHEN** an old subject has an invalid alunos_id and has never been mirrored for the user
- **THEN** the mirror SHALL synchronize valid records belonging to the user without modifying the old subject.

### Requirement: Preserve known records with broken links
The system SHALL reject a snapshot that loses a known user's ownership link before local mutations.

#### Scenario: Existing mirrored subject loses its owner
- **WHEN** the remote subject previously mirrored for a user has no valid owner reference
- **THEN** synchronization SHALL fail and preserve the previous local data.

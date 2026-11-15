# Xano Export Security Specification

## Purpose
Prepare the real Portuguese academic CRUD for server-only access without destructive workspace operations.

## ADDED Requirements

### Requirement: Guard academic endpoints
The system SHALL validate the backend service credential before every academic database operation.

#### Scenario: Missing server credential
- **WHEN** an academic endpoint receives no valid service credential
- **THEN** it SHALL reject the request before querying or changing records.

### Requirement: Preserve selective PATCH semantics
The system SHALL update only explicitly supplied mutable fields and SHALL retain an explicit null deadline.

#### Scenario: Clear a deadline
- **WHEN** a trusted backend sends prazo as null
- **THEN** the update SHALL clear the deadline rather than silently dropping the field.

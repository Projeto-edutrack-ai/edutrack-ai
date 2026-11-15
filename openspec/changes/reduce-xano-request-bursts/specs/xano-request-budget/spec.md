# Xano Request Budget Specification

## Purpose
Reduzir chamadas repetidas e tratar limite de requisições sem perda aparente de dados.

## ADDED Requirements

### Requirement: Coalesce remote reads
The system SHALL share fresh reads within a backend process while retaining caller authorization and invalidating reads on mutation.

#### Scenario: Concurrent requests for the same list
- **WHEN** several views request the same list concurrently
- **THEN** the backend SHALL issue one remote GET and return independent copies.

### Requirement: Pause on remote rate limiting
The system SHALL return HTTP 429 during a remote cooldown without retrying writes.

#### Scenario: Xano rejects a mutation with 429
- **WHEN** the remote service rate limits a mutation
- **THEN** the backend SHALL report the pause and SHALL NOT replay the mutation automatically.

### Requirement: Preserve visible records on refresh failure
The interface SHALL keep existing subject cards with an explicit refresh warning.

#### Scenario: A subject refresh is rate limited
- **WHEN** a previously loaded list cannot be refreshed
- **THEN** its cards SHALL remain visible and the interface SHALL identify the failed refresh.

# Portuguese Search Specification

## Purpose
Pesquisar registros do usuário sem diferenças de acento, caixa ou composição Unicode.

## ADDED Requirements

### Requirement: Normalize Portuguese search in SQLite
The system SHALL match equivalent Portuguese text across case, accents and Unicode composition without modifying stored values.

#### Scenario: Search for an accented subject
- **WHEN** the user searches for Integração or Integracao
- **THEN** matching owned subjects and tasks SHALL be returned regardless of NFC/NFD storage.

### Requirement: Keep search results above page content
The interface SHALL display the results dropdown above animated page sections.

#### Scenario: Search from the dashboard
- **WHEN** the results dropdown is visible
- **THEN** dashboard content SHALL NOT obscure its buttons.

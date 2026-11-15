# Xano Readonly Diagnostics Specification

## Purpose
Obter o motivo de falha do espelho sem repetir mutações nem expor credenciais.

## ADDED Requirements

### Requirement: Diagnose without mutation or personal data
The diagnostic SHALL read contract metadata without creating, editing or deleting records and SHALL output only IDs, counts and issue codes.

#### Scenario: A legacy record has no owner
- **WHEN** a returned subject has no valid alunos_id
- **THEN** the report SHALL identify its record ID without exposing student names or emails.

# Reviewed GitHub Delivery Specification

## Purpose
Versionar correções de forma revisável sem expor configuração privada nem sobrescrever histórico remoto.

## ADDED Requirements

### Requirement: Prepare reviewed source changes
The delivery SHALL contain source changes on a separate branch and SHALL exclude credentials, local databases and installed dependencies.

#### Scenario: Apply changes to the public repository
- **WHEN** the student prepares the delivery from a clean clone
- **THEN** the patch SHALL apply against the reviewed base and SHALL require review before push and merge.

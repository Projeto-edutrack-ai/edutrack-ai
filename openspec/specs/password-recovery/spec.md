# password-recovery Specification

## Purpose

Proteger a recuperação de acesso mediante token de uso único com validade limitada, mantendo a resposta genérica para endereços conhecidos e desconhecidos.

## Requirements

### Requirement: Password reset by e-mail token
O sistema SHALL enviar por e-mail um link com token de uso único e validade limitada quando um e-mail cadastrado solicitar recuperação de senha, e MUST NOT revelar se o e-mail existe.

#### Scenario: E-mail cadastrado
- **WHEN** o aluno solicita recuperação com um e-mail cadastrado
- **THEN** o sistema envia uma mensagem contendo o link de redefinição e responde com mensagem genérica

#### Scenario: E-mail desconhecido
- **WHEN** o aluno solicita recuperação com um e-mail não cadastrado
- **THEN** o sistema responde com a mesma mensagem genérica e não envia e-mail

### Requirement: Password reset with valid token
O sistema SHALL redefinir a senha somente com token válido, não expirado e não usado, e MUST invalidar o token após o uso.

#### Scenario: Token válido
- **WHEN** o aluno envia token válido e nova senha
- **THEN** a senha é atualizada e o token não pode ser reutilizado

#### Scenario: Token inválido ou expirado
- **WHEN** o aluno envia token inválido, expirado ou já usado
- **THEN** o sistema responde 400 e a senha não muda

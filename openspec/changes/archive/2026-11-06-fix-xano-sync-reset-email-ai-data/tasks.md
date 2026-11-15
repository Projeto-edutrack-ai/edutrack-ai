## 1. Xano

- [x] 1.1 Cliente CRUD do Xano e `ensure_aluno` por e-mail
- [x] 1.2 Sincronização no cadastro/login e endpoint `POST /auth/xano-sync`
- [x] 1.3 Espelho de disciplinas e tarefas (`xano_id`) + migração
- [x] 1.4 Analytics, IA e relatório usam o espelho

## 2. Recuperação de senha

- [x] 2.1 Tabela de tokens, serviço de e-mail e novos endpoints
- [x] 2.2 Frontend: solicitação por e-mail e tela de nova senha via link

## 3. IA

- [x] 3.1 Corrigir `total_time_spent_hours` e modelo Gemini configurável
- [x] 3.2 Cronômetro grava tempo por ID do Xano

## 4. Validação

- [x] 4.1 Testes com banco temporário (sem apagar `edutrack.db`)
- [x] 4.2 Testes novos: sync Xano, e-mail/token, espelho, IA
- [x] 4.3 Teste real de SMTP com servidor local (aiosmtpd) e e2e com Xano falso em HTTP
- [x] 4.4 Atualizar README, `.env.example` e `openspec validate`

## Resultado da validação

- `python -m pytest`: 100 testes aprovados (86 anteriores + 14 novos), com banco temporário.
- Execução ponta a ponta com servidor real + Xano falso em HTTP: cadastro cria o aluno, o e-mail de recuperação é gerado, o token redefine a senha uma única vez e o login com a nova senha funciona.
- **Não validado**: Xano real e SMTP real do provedor (sem acesso de rede/credenciais neste ambiente); o frontend foi verificado só por `node --check`, sem teste em navegador.

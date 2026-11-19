# Corrigir integração Xano e fluxos acadêmicos do EduTrack

O CRUD acadêmico passa pelo FastAPI autenticado, com vínculo persistente do aluno e verificação de propriedade. A revisão corrige inicialização dos formulários, rajadas de chamadas ao Xano, sincronização bloqueada por registros sem dono e busca em português. Remove a integração Classroom por decisão do grupo e preserva a interface, o mentor e os recursos de estudo.

## Validação
- 83 testes Python e 11 testes JavaScript passaram no clone preparado.
- OpenSpec validado em modo estrito.
- Com a aluna: CRUD real, cronômetro/progresso, PDF, busca nome OU atraso e GET de matéria/tarefa de outra conta bloqueado com 404.
- Push das 15 rotas Xano realizado pela aluna; acesso sem chave negado em teste real.

## Pendências de entrega
A busca e o PDF funcionam pela interface/FastAPI, mas os endpoints iniciados no Xano das atividades 14/15 e o serviço Python HTTPS ainda precisam ser configurados. O CRUD Xano é protegido por credencial de servidor; identidade e autorização individual permanecem no FastAPI, sem presumir auth.id nativo no Xano. Figma, demonstração do agente, relatório final e evidências da disciplina permanecem em revisão.

Não contém .env, banco local, credenciais, dependências instaladas ou PDF com dados pessoais. Não considerar este PR confirmação de conclusão de todas as 16 atividades.

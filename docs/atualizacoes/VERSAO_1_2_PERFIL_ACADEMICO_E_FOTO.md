# 👤 Atualização v1.2 — Foto de Perfil, Presets & Dados Acadêmicos

> **Status:** Concluído & Integrado  
> **Escopo:** Backend (Migração de Schema e API), Frontend (Modal de Perfil e Sidebar Card)

---

## 1. Contexto da Atualização
O estudante solicitou a funcionalidade de **personalização total do perfil**: poder carregar uma foto, escolher fotos rápidas, alterar seu nome completo, ano/semestre da faculdade, curso de graduação, nome da universidade e biografia/foco de estudos.

---

## 2. O Que Mudou Nesta Versão

### 2.1. Alterações no Banco de Dados & Schemas (Backend)
- **Extensão da Tabela `users`:** Adicionadas 5 novas colunas:
  - `avatar_url` (`Text`): Permite armazenar tanto URLs remotas quanto imagens em Base64 Data URI de até 2MB.
  - `course` (`String(100)`): Curso superior do aluno (ex: Ciência da Computação).
  - `college_year` (`String(50)`): Ano/semestre atual (ex: 3º Ano / 6º Semestre).
  - `institution` (`String(150)`): Nome da faculdade ou universidade.
  - `bio` (`String(255)`): Descrição dos objetivos acadêmicos.
- **Novo Endpoint `PUT /api/auth/profile`:** Rota protegida por JWT que recebe o payload com os dados atualizados, valida duplicidade de e-mail e salva as modificações no banco de dados.
- **Compatibilidade Pydantic v2:** Migração de configurações legadas para `ConfigDict(from_attributes=True)`.

### 2.2. Modal de Perfil Redesenhado em Duas Colunas (Frontend)
- **Painel Esquerdo (Avatar):**
  - Exibição da foto atual em tamanho grande (96x96px) com indicador luminoso de status online.
  - Botão de envio de foto do computador via `FileReader` para Base64.
  - Botão de remover foto com retorno automático para as iniciais do estudante.
  - 4 botões de avatares pré-selecionados (Unsplash) para troca com 1 único clique.
- **Painel Direito (Informações do Estudante):**
  - Seções organizadas com cabeçalhos sutis: "Identidade" e "Informações Acadêmicas".
  - Entradas para Nome, Bio, Curso, Ano/Semestre, Turno e Faculdade.

### 2.3. Sincronização Dinâmica na Sidebar
- O card do usuário no rodapé da barra lateral passa a exibir a foto real do aluno ou suas iniciais monogramadas.
- Exibe o curso e o ano letivo diretamente abaixo do nome.
- Ao clicar no card, abre instantaneamente o modal de edição de perfil.

---

## 3. Arquivos Impactados
- `backend/app/models/user.py`: Inclusão das novas colunas.
- `backend/app/schemas/user.py`: Criação de `UserUpdate` e atualização de `UserResponse`.
- `backend/app/api/auth.py`: Criação do endpoint `PUT /auth/profile`.
- `frontend/index.html`: Inclusão do modal `#modal-profile-overlay` e atualização do card `#sidebar-user-card`.
- `frontend/js/auth.js`: Lógica de upload em Base64, binding dos presets e chamada de API.
- `tests/test_api.py`: Novo teste unitário automatizado `test_update_user_profile`.

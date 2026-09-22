# 👤 Tela 06 — Perfil Acadêmico do Estudante

> **Módulo:** Identidade & Personalização do Aluno  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 764–880), `frontend/js/auth.js`, `backend/app/models/user.py`, `backend/app/api/auth.py`

---

## 1. Visão Geral
O modal de **Perfil Acadêmico** do EduTrack AI oferece uma central completa de customização e identificação do estudante. Inspirado nos padrões de interface do *Linear* e *Notion Settings*, possui layout dividido em dois painéis organizados para foto de perfil e dados acadêmicos.

---

## 2. Componentes e Funcionalidades

### 2.1. Painel Esquerdo — Foto de Perfil & Presets
- **Pré-visualização Ampla da Foto:** Avatar com borda arredondada, sombra suave e indicador de status online em tempo real.
- **Upload Direto de Arquivo:**
  - Suporte a imagens PNG, JPG ou GIF de até 2MB.
  - Conversão instantânea via `FileReader` para Base64 Data URI com salvamento no banco de dados.
- **Remover Foto:** Retorna automaticamente ao avatar padrão com monograma das iniciais do aluno (ex: `LF`).
- **Avatares Rápidos (Presets):** 4 opções de avatares com fotos pré-definidas para seleção com apenas 1 clique.

### 2.2. Painel Direito — Dados Pessoais & Acadêmicos
1. **Seção Identidade:**
   - **Nome Completo (obrigatório):** Atualiza imediatamente a exibição no cabeçalho e na barra lateral.
   - **Bio / Foco de Estudos:** Campo multilinha para metas de carreira ou áreas de interesse (ex: "Foco em IA e Engenharia de Software").
2. **Seção Informações Acadêmicas:**
   - **Curso de Graduação:** Ex: "Ciência da Computação".
   - **Ano / Semestre:** Ex: "3º Ano / 6º Semestre".
   - **Turno:** Seletor com opções (Matutino, Vespertino, Noturno, Integral, EAD).
   - **Faculdade / Universidade:** Nome da instituição de ensino superior.

### 2.3. Sincronização em Tempo Real
- Ao clicar em "Salvar Perfil", a API atualiza os registros do estudante e reflete as alterações imediatamente em toda a aplicação:
  - Foto e nome no card da barra lateral.
  - Informações acadêmicas exibidas no rodapé da navegação.
  - Notificação de confirmação via `Toast`.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** O layout em duas colunas colapsa elegantemente para um fluxo vertical único com rolagem interna suave, mantendo todos os botões de ação e campos confortáveis para preenchimento.
- **Desktop (>= 1024px):** Layout elegante dividido em duas colunas (`max-w-2xl`) com separadores visuais refinados.

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/auth/me` | Recupera os dados completos do perfil do aluno autenticado |
| `PUT` | `/api/auth/profile` | Atualiza foto, nome, curso, ano, faculdade e biografia |

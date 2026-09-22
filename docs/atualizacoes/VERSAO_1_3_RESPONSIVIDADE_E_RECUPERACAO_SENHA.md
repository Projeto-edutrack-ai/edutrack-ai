# 📱 Atualização v1.3 — Responsividade Total & Modal de Esqueci Minha Senha

> **Status:** Concluído & Testado  
> **Escopo:** Frontend, CSS Media Queries, Acessibilidade Mobile e Fluxo de Autenticação

---

## 1. Contexto da Atualização
O usuário solicitou:
1. **Um modal profissional para recuperação de senha ("Esqueci minha senha")** em substituição a qualquer janela simples do navegador.
2. **Responsividade total em todas as telas da aplicação**, garantindo usabilidade em smartphones e tablets.

---

## 2. O Que Mudou Nesta Versão

### 2.1. Novo Modal Interativo de Recuperação de Senha
- **Componente Criado:** `#modal-forgot-password-overlay`.
- **Experiência do Usuário (UX):**
  - Card centralizado com efeito *glassmorphism* e animação de entrada `modal-animate-in`.
  - Herança inteligente: se o usuário já preencheu o e-mail no formulário de login, o e-mail é automaticamente inserido no campo de recuperação.
  - Conexão em tempo real com o backend (`POST /api/auth/forgot-password`).
  - Estado de carregamento no botão (`Enviando...`) e alerta de confirmação em tela.
  - Fechamento suave via botão X, botão Cancelar, clique fora da caixa ou após envio bem-sucedido.

### 2.2. Responsividade Mobile (< 768px)
- **Barra de Navegação Inferior (Bottom Nav Mobile):**
  - Inclusão do botão **"Perfil"**, permitindo que em celulares o usuário edite seus dados com um único toque.
  - Aplicação de `env(safe-area-inset-bottom)` para suporte nativo a aparelhos com entalhe ou barra gestual (iOS/Android).
- **Cards de Indicadores (KPIs):** Ajustados para layout em duas colunas (2x2) no mobile, evitando quebras de texto.
- **Prevenção de Zoom no iOS:** Entradas de formulário (`input`, `select`, `textarea`) ajustadas para `16px`, prevenindo o zoom automático incômodo do navegador Safari.
- **Ergonomia de Toque:** Aplicação da diretriz de acessibilidade com área de toque mínima de `44x44px` para todos os botões e links.
- **Modais com Rolagem Interna:** Todos os modais (`Profile`, `Subjects`, `Tasks`, `Forgot Password`, `Auth`) ganharam `max-height: 90vh` com rolagem vertical interna, impedindo que partes do formulário fiquem inacessíveis em telas pequenas.

---

## 3. Arquivos Impactados
- `frontend/index.html`: Inserção do `#modal-forgot-password-overlay` e inclusão do botão de Perfil na barra móvel.
- `frontend/js/auth.js`: Adição de todos os manipuladores de evento e chamadas de API do modal de recuperação de senha.
- `frontend/css/styles.css`: Atualização profunda do bloco `@media (max-width: 767px)`.

# Design

Auth.bindEvents já contém eventos do perfil, recuperação de senha e login. Não criar outra função vazia nem duplicar listeners. Remover somente this.bindProfileEvents() mantém esse fluxo. Testar os módulos reais com um DOM mínimo e API simulada, pois testes anteriores do cliente HTTP isolado não exercitavam a inicialização.

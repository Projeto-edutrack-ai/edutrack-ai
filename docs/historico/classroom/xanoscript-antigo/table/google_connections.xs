// Conexão OAuth do usuário com a conta Google (uma conexão por usuário).
// Não existe campo de senha do Google: o OAuth entrega apenas tokens.
// Os tokens são guardados CIFRADOS (colunas *_enc), nunca em texto puro.
table google_connections {
  schema {
    int id
    timestamp created_at?=now
    timestamp updated_at?=now
  
    // Dono da conexão (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    // Identificador estável da conta Google (claim "sub")
    text google_sub filters=trim
    email? google_email? filters=trim|lower
  
    // Ciphertext produzido pelo Xano com chave em variável de ambiente.
    // O campo password do Xano não serve aqui: ele é hash e o token precisa ser recuperável.
    text? access_token_enc?
    text? refresh_token_enc?
    timestamp? token_expires_at?
  
    // Escopos concedidos, separados por espaço (como o Google retorna)
    text? scopes?
  
    enum status?=active {
      values = ["active", "needs_reauth", "revoked", "error"]
    }
  
    timestamp connected_at?=now
    timestamp? last_refreshed_at?
    text? last_error?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "owner_id", op: "asc"}]}
    {type: "btree", field: [{name: "google_sub", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]

  tags = ["classroom"]
}

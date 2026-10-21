// Estados (state) do fluxo OAuth do Google: anti-CSRF, de uso único e com validade curta.
// O Xano grava o nonce em /oauth/google/start e o valida/consome em /oauth/google/callback.
table oauth_states {
  schema {
    int id
    timestamp created_at?=now
  
    // Usuário que iniciou o fluxo (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    // Valor aleatório não previsível enviado ao Google como "state"
    text nonce filters=trim
  
    // Para onde devolver o navegador no fim; precisa estar na lista de URLs permitidas do Xano
    text return_url
  
    // Validade curta (ex.: 10 minutos). Expirado ou já usado = rejeitar
    timestamp expires_at
    timestamp? used_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "nonce", op: "asc"}]}
    {type: "btree", field: [{name: "owner_id", op: "asc"}]}
    {type: "btree", field: [{name: "expires_at", op: "asc"}]}
  ]

  tags = ["classroom"]
}

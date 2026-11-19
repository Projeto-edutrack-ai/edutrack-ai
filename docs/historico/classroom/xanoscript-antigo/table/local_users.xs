// Espelho do usuário local do EduTrack (FastAPI) no Xano.
// NÃO é a tabela de autenticação nativa "user" do Xano e não guarda senha.
// local_user_id = users.id do FastAPI/SQLite (identificador único da integração).
table local_users {
  schema {
    int id
    timestamp created_at?=now
    timestamp updated_at?=now
  
    // users.id no FastAPI (não confundir com local_users.id, a PK interna do Xano)
    int local_user_id
  
    // Cópia informativa; a identidade é local_user_id (o e-mail pode mudar no FastAPI)
    email? email? filters=trim|lower
    text? name?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "local_user_id", op: "asc"}]}
    {type: "btree", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["classroom"]
}

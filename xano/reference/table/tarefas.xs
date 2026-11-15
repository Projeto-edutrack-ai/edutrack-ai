table tarefas {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int materias_id? {
      table = "materias"
    }
  
    text titulo_? filters=trim
    text descricao? filters=trim
    timestamp? prazo?
    enum status? {
      values = ["pendente", "em_andamento ", "concluida"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "hOR8QqwjcWYtD9d74VtzsMA93UY"
}
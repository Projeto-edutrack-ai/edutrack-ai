table materias {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int alunos_id? {
      table = "alunos"
    }
  
    text nome? filters=trim
    text professor? filters=trim
    text descricao? filters=trim
    int carga_horaria?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "-uwua4uJDqrOwAkx9iPJYhwhG3s"
}
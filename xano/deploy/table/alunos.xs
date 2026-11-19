table alunos {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    text nome? filters=trim
    email email? filters=trim|lower
    text curso? filters=trim
    int semestre?
    int? user_id? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "Hyj1_MqV8SwfIgYq86fQ4I0PPuM"
}

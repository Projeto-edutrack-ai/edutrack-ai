// List materias owned by the authenticated Xano user
query "privado/materias" verb=GET {
  api_group = "edutrack privado"
  auth = "user"

  input {
  }

  stack {
    db.get alunos {
      field_name = "user_id"
      field_value = $auth.id
    } as $aluno

    precondition ($aluno != null) {
      error_type = "accessdenied"
      error = "No linked student is available for this user."
    }

    db.query materias {
      where = $db.materias.alunos_id == $aluno.id
      return = {type: "list"}
    } as $materias
  }

  response = $materias
  guid = "XSwY7-YAR19nDFwF1uuA908Trbg"
}

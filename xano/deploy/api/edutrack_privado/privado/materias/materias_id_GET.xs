// Get an owned materia by ID
query "privado/materias/{materias_id}" verb=GET {
  api_group = "edutrack privado"
  auth = "user"

  input {
    int materias_id? filters=min:1
  }

  stack {
    db.get materias {
      field_name = "id"
      field_value = $input.materias_id
    } as $materia

    precondition ($materia != null) {
      error_type = "notfound"
      error = "Not Found."
    }

    db.get alunos {
      field_name = "id"
      field_value = $materia.alunos_id
    } as $aluno

    precondition ($aluno != null && $aluno.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $materia
  guid = "yMW6R-11qANJj8FIeh0UEm03n4U"
}

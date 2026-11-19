// Update an owned materia without changing its owner
query "privado/materias/{materias_id}" verb=PATCH {
  api_group = "edutrack privado"
  auth = "user"

  input {
    int materias_id? filters=min:1
    text nome?
    text professor?
    text descricao?
    int carga_horaria?
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

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input

    db.patch materias {
      field_name = "id"
      field_value = $input.materias_id
      data = `$input|pick:($raw_input|keys)`|pick:["nome", "professor", "descricao", "carga_horaria"]
    } as $materia
  }

  response = $materia
  guid = "G4-2vdk3fnzfwdORRceIMOPGROo"
}

// Create a materia for the authenticated Xano user's linked student
query "privado/materias" verb=POST {
  api_group = "edutrack privado"
  auth = "user"

  input {
    text nome?
    text professor?
    text descricao?
    int carga_horaria?
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

    db.add materias {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        alunos_id: $aluno.id
        nome: $input.nome
        professor: $input.professor
        descricao: $input.descricao
        carga_horaria: $input.carga_horaria
      }
    } as $materias
  }

  response = $materias
  guid = "otaIkSlfb5cDZ5mtYx1hgWS_Prg"
}

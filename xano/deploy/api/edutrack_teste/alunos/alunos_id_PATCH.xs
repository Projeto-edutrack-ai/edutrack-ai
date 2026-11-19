// Edit alunos record
query "alunos/{alunos_id}" verb=PATCH {
  api_group = "edutrack teste"

  input {
    int alunos_id? filters=min:1
    dblink {
      table = "alunos"
    }
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch alunos {
      field_name = "id"
      field_value = $input.alunos_id
      data = `$input|pick:($raw_input|keys)`|pick:["nome", "email", "curso", "semestre"]
    } as $alunos
  }

  response = $alunos
  guid = "8fnhVyb459-88VODzUSITeQBmeY"
}
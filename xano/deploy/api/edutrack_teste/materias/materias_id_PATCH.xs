// Edit materias record
query "materias/{materias_id}" verb=PATCH {
  api_group = "edutrack teste"

  input {
    int materias_id? filters=min:1
    dblink {
      table = "materias"
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
  
    db.patch materias {
      field_name = "id"
      field_value = $input.materias_id
      data = `$input|pick:($raw_input|keys)`|pick:["alunos_id", "nome", "professor", "descricao", "carga_horaria"]
    } as $materias
  }

  response = $materias
  guid = "ROWeTCllpWwv6WrH1rD2ORUYxxE"
}
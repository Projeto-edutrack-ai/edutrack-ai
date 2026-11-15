// Edit tarefas record
query "tarefas/{tarefas_id}" verb=PATCH {
  api_group = "edutrack teste"

  input {
    int tarefas_id? filters=min:1
    dblink {
      table = "tarefas"
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
  
    db.patch tarefas {
      field_name = "id"
      field_value = $input.tarefas_id
      data = `$input|pick:($raw_input|keys)`|pick:["materias_id", "titulo_", "descricao", "prazo", "status"]
    } as $tarefas
  }

  response = $tarefas
  guid = "N9NreiBWN4G_ViBRgTDw26PIUss"
}
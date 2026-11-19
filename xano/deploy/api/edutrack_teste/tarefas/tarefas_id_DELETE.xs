// Delete tarefas record.
query "tarefas/{tarefas_id}" verb=DELETE {
  api_group = "edutrack teste"

  input {
    int tarefas_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.del tarefas {
      field_name = "id"
      field_value = $input.tarefas_id
    }
  }

  response = null
  guid = "B4BtTmoNXZQ1sNpXO8q6YLs284E"
}
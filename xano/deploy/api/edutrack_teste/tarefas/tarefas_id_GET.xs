// Get tarefas record
query "tarefas/{tarefas_id}" verb=GET {
  api_group = "edutrack teste"

  input {
    int tarefas_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.get tarefas {
      field_name = "id"
      field_value = $input.tarefas_id
    } as $tarefas
  
    precondition ($tarefas != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $tarefas
  guid = "b2UdWaX4tKcnC7TRI8vMWz3wJLg"
}
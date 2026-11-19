// Add tarefas record
query tarefas verb=POST {
  api_group = "edutrack teste"

  input {
    dblink {
      table = "tarefas"
    }
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.add tarefas {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $tarefas
  }

  response = $tarefas
  guid = "xNvLjTz5TDtDXwov-ObiUZqDjmM"
}
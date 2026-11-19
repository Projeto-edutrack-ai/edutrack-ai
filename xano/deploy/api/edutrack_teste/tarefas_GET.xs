// Query all tarefas records
query tarefas verb=GET {
  api_group = "edutrack teste"

  input {
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.query tarefas {
      return = {type: "list"}
    } as $tarefas
  }

  response = $tarefas
  guid = "y1-A5OLSw9KYdiET3e1zTddjCHI"
}
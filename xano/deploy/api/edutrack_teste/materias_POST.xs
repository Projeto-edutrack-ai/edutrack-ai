// Add materias record
query materias verb=POST {
  api_group = "edutrack teste"

  input {
    dblink {
      table = "materias"
    }
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.add materias {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $materias
  }

  response = $materias
  guid = "Kg3OCsBonmERVEJKjdlhvMJQf_Q"
}
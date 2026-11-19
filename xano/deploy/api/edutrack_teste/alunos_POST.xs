// Add alunos record
query alunos verb=POST {
  api_group = "edutrack teste"

  input {
    dblink {
      table = "alunos"
    }
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.add alunos {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $alunos
  }

  response = $alunos
  guid = "Gw5bMm3Q0_XhZV7K_egg-uYIFfM"
}
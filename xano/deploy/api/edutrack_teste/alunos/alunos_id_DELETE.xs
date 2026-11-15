// Delete alunos record.
query "alunos/{alunos_id}" verb=DELETE {
  api_group = "edutrack teste"

  input {
    int alunos_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.del alunos {
      field_name = "id"
      field_value = $input.alunos_id
    }
  }

  response = null
  guid = "woFOQYGMHaVHRYmumUlbk1VrZ7Y"
}
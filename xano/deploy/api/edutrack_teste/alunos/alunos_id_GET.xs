// Get alunos record
query "alunos/{alunos_id}" verb=GET {
  api_group = "edutrack teste"

  input {
    int alunos_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.get alunos {
      field_name = "id"
      field_value = $input.alunos_id
    } as $alunos
  
    precondition ($alunos != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $alunos
  guid = "VjChLZB9soX7_1EGfw66oPHxnew"
}
// Get materias record
query "materias/{materias_id}" verb=GET {
  api_group = "edutrack teste"

  input {
    int materias_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.get materias {
      field_name = "id"
      field_value = $input.materias_id
    } as $materias
  
    precondition ($materias != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $materias
  guid = "xM3LTkZjUn4kAyhG-PGuAbhVJZE"
}
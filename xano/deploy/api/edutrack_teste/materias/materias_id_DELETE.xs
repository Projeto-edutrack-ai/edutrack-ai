// Delete materias record.
query "materias/{materias_id}" verb=DELETE {
  api_group = "edutrack teste"

  input {
    int materias_id? filters=min:1
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.del materias {
      field_name = "id"
      field_value = $input.materias_id
    }
  }

  response = null
  guid = "9bahgh8P6mEknX5yVWx81GeHZ0o"
}
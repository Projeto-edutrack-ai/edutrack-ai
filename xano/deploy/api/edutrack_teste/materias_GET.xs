// Query all materias records
query materias verb=GET {
  api_group = "edutrack teste"

  input {
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.query materias {
      return = {type: "list"}
    } as $materias
  }

  response = $materias
  guid = "asdho-QowkQ6gK2W3Mji0-Tn4kY"
}
// Query all alunos records
query alunos verb=GET {
  api_group = "edutrack teste"

  input {
  }

  stack {
    // Server-to-server guard; never expose this credential in the frontend.
    function.run "auth/validate_api_key" {
      input = {}
    } as $service_authorized

    db.query alunos {
      return = {type: "list"}
    } as $alunos
  }

  response = $alunos
  guid = "k7gz5AY4WptNfVStLxhJNvvg0_Q"
}
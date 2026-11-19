// Validates server-to-server calls from EduTrack FastAPI using X-API-Key
function "auth/validate_api_key" {
  input {
  }

  stack {
    // Reject immediately if server secret XANO_API_KEY is not configured or empty
    precondition ($env.XANO_API_KEY != null && $env.XANO_API_KEY != "") {
      error_type = "accessdenied"
      error = "Acesso negado: autenticação do servidor indisponível."
    }
  
    // Extract API key from incoming request headers
    var $api_key {
      value = ($env.$http_headers["x-api-key"] ?? $env.$http_headers["X-API-Key"] ?? $env.$http_headers["X-Api-Key"] ?? $env.$http_headers["x_api_key"] ?? "")|to_text
    }
  
    // Strictly compare provided header with configured secret without exposing key values
    precondition ($api_key != "" && $api_key === $env.XANO_API_KEY) {
      error_type = "accessdenied"
      error = "Acesso negado: credencial X-API-Key inválida ou ausente."
    }
  }

  response = true
  guid = "V_ud1kngTJ96IRzxtayNRWfX0uQ"
}
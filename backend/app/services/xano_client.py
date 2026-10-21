"""Cliente HTTP do Xano (grupo de API ``integration``) para os dados do Google Classroom.

Configuração por variáveis de ambiente (ver .env.example):
    XANO_BASE_URL         URL base do API group, sem barra final
    XANO_API_KEY          chave enviada no cabeçalho X-API-Key (nunca vai ao frontend nem aos logs)
    XANO_TIMEOUT_SECONDS  timeout por requisição (padrão 15)
    XANO_SYNC_TIMEOUT_SECONDS  timeout da sincronização com o Google via Xano (padrão 60)

Contrato dos endpoints (a serem criados no Xano em etapa futura) em
openspec/specs/xano-classroom-contract.md. Nada aqui contacta o Google: o Xano é o único elo.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx

from app.core.config import settings

API_KEY_HEADER = "X-API-Key"
_MAX_DETAIL_CHARS = 200


class XanoError(Exception):
    """Erro base de qualquer falha na comunicação com o Xano."""


class XanoConfigError(XanoError):
    """XANO_BASE_URL/XANO_API_KEY ausentes ou inválidos."""


class XanoTimeoutError(XanoError):
    """O Xano não respondeu dentro do tempo limite."""


class XanoConnectionError(XanoError):
    """Falha de rede ao chamar o Xano (DNS, conexão recusada etc.)."""


class XanoHTTPError(XanoError):
    """O Xano respondeu com status HTTP de erro (>= 300)."""

    def __init__(self, status_code: int, detail: str = ""):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Xano respondeu HTTP {status_code}" + (f": {detail}" if detail else ""))


class XanoInvalidResponseError(XanoError):
    """A resposta não é JSON válido ou não segue o contrato esperado."""


class XanoClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        transport: Optional[httpx.BaseTransport] = None,
        sync_timeout: Optional[float] = None,
    ):
        self._base_url = (settings.XANO_BASE_URL if base_url is None else base_url) or ""
        self._api_key = (settings.XANO_API_KEY if api_key is None else api_key) or ""
        self._timeout = settings.XANO_TIMEOUT_SECONDS if timeout is None else timeout
        self._sync_timeout = settings.XANO_SYNC_TIMEOUT_SECONDS if sync_timeout is None else sync_timeout
        self._transport = transport  # injetável nos testes (httpx.MockTransport)

    # ------------------------------------------------------------------ API pública

    def is_configured(self) -> bool:
        """True se XANO_BASE_URL e XANO_API_KEY estão definidas e válidas (sem fazer requisição)."""
        try:
            self._configured_base_url()
        except XanoConfigError:
            return False
        return True

    def start_oauth(self, local_user_id: int, return_url: str) -> str:
        """Pede ao Xano a URL de consentimento do Google (o Xano gera e valida o ``state``).

        ``return_url`` é para onde o Xano devolve o navegador após o callback; o Xano só aceita
        URLs da sua lista de permissão.
        """
        data = self._request(
            "POST", "/oauth/google/start",
            json_body={"local_user_id": _user_id(local_user_id), "return_url": return_url},
        )
        url = data.get("authorization_url") if isinstance(data, dict) else None
        if not isinstance(url, str) or not url.lower().startswith("https://"):
            raise XanoInvalidResponseError("o Xano não devolveu 'authorization_url' (https) válida")
        return url

    def disconnect(self, local_user_id: int) -> Dict[str, Any]:
        """Revoga/apaga a conexão Google do usuário no Xano (não toca nos dados locais)."""
        data = self._request("DELETE", "/classroom/connection", params={"local_user_id": _user_id(local_user_id)})
        if not isinstance(data, dict):
            raise XanoInvalidResponseError("resposta de desconexão do Xano deve ser um objeto JSON")
        return data

    def get_status(self, local_user_id: int) -> Dict[str, Any]:
        """Estado da conexão do usuário com o Classroom (objeto JSON)."""
        data = self._request("GET", "/classroom/status", params={"local_user_id": _user_id(local_user_id)})
        if not isinstance(data, dict):
            raise XanoInvalidResponseError("status do Xano deve ser um objeto JSON")
        return data

    def get_courses(self, local_user_id: int) -> List[Dict[str, Any]]:
        """Cursos do usuário conhecidos pelo Xano. Aceita lista pura ou {"courses": [...]}."""
        data = self._request("GET", "/classroom/courses", params={"local_user_id": _user_id(local_user_id)})
        if isinstance(data, dict):
            data = data.get("courses")
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise XanoInvalidResponseError("lista de cursos do Xano inválida")
        return data

    def get_export(
        self, local_user_id: int, since: Optional[Union[datetime, str]] = None
    ) -> Dict[str, Any]:
        """Export canônico (cursos -> atividades -> entrega) já no formato EduTrack."""
        params: Dict[str, Any] = {"local_user_id": _user_id(local_user_id)}
        if since is not None:
            params["since"] = since.isoformat() if isinstance(since, datetime) else str(since)
        data = self._request("GET", "/classroom/export", params=params)
        if not isinstance(data, dict) or not isinstance(data.get("courses"), list):
            raise XanoInvalidResponseError("export do Xano deve ser um objeto com a lista 'courses'")
        return data

    def start_sync(self, local_user_id: int) -> Dict[str, Any]:
        """Pede ao Xano que sincronize com o Classroom (o Xano fala com o Google)."""
        data = self._request("POST", "/classroom/sync", json_body={"local_user_id": _user_id(local_user_id)},
                             timeout=self._sync_timeout)
        if not isinstance(data, dict):
            raise XanoInvalidResponseError("resposta de sincronização do Xano deve ser um objeto JSON")
        return data

    # ------------------------------------------------------------------ interno

    def _configured_base_url(self) -> str:
        base = self._base_url.strip().rstrip("/")
        if not base or not base.lower().startswith(("http://", "https://")):
            raise XanoConfigError("XANO_BASE_URL não configurada ou inválida (use http:// ou https://)")
        if not self._api_key.strip():
            raise XanoConfigError("XANO_API_KEY não configurada")
        return base

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        base = self._configured_base_url()
        headers = {"Accept": "application/json", API_KEY_HEADER: self._api_key}
        try:
            with httpx.Client(timeout=self._timeout if timeout is None else timeout, transport=self._transport) as http:
                response = http.request(method, f"{base}{path}", params=params, json=json_body, headers=headers)
        except httpx.TimeoutException as exc:
            raise XanoTimeoutError(f"Timeout ao chamar o Xano ({method} {path})") from exc
        except httpx.InvalidURL as exc:
            raise XanoConfigError("XANO_BASE_URL inválida") from exc
        except httpx.RequestError as exc:
            raise XanoConnectionError(f"Falha de conexão com o Xano ({method} {path})") from exc

        if response.status_code >= 300:
            raise XanoHTTPError(response.status_code, _error_detail(response))

        try:
            return response.json()
        except ValueError as exc:  # JSONDecodeError e UnicodeDecodeError
            raise XanoInvalidResponseError(f"Resposta do Xano não é JSON válido ({method} {path})") from exc


def _user_id(local_user_id: Any) -> int:
    if isinstance(local_user_id, bool) or not isinstance(local_user_id, int) or local_user_id <= 0:
        raise ValueError("local_user_id deve ser um inteiro positivo")
    return local_user_id


def _error_detail(response: httpx.Response) -> str:
    """Mensagem curta do erro do Xano (campo 'message'/'detail' ou trecho do corpo)."""
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        for key in ("message", "detail", "error"):
            if isinstance(body.get(key), str):
                return body[key][:_MAX_DETAIL_CHARS]
        return json.dumps(body, ensure_ascii=False)[:_MAX_DETAIL_CHARS]
    return (response.text or "")[:_MAX_DETAIL_CHARS]

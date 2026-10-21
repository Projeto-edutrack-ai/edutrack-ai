"""Xano falso (httpx.MockTransport) para os testes; sem credenciais reais."""
import json

import httpx

from app.services.xano_client import API_KEY_HEADER, XanoClient
from classroom_helpers import make_export

TEST_BASE_URL = "https://xano.test/api:integration"
TEST_API_KEY = "test-key-not-real"


class FakeXano:
    """Xano falso baseado em httpx.MockTransport. Guarda um export por usuário e responde por caminho."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth?client_id=FAKE&state=FAKE"

    def __init__(self):
        self.exports = {}
        self.calls = []
        self.statuses = {}      # user_id -> payload de /classroom/status
        self.sync_payload = {"status": "success", "courses": 1, "coursework": 1, "submissions": 1, "errors": []}
        self.courses = {}       # user_id -> lista de /classroom/courses
        self.disconnected = []
        self.mode = None  # None | "500" | "401" | "409" | "timeout" | "connect" | "not_json" | "list" | "no_courses" | "no_auth_url"

    def _user_id(self, request: httpx.Request) -> int:
        if "local_user_id" in request.url.params:
            return int(request.url.params["local_user_id"])
        return int(json.loads(request.content)["local_user_id"])

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        assert request.headers.get(API_KEY_HEADER) == TEST_API_KEY
        user_id = self._user_id(request)
        path = request.url.path
        if self.mode == "500":
            return httpx.Response(500, json={"message": "erro interno do xano"})
        if self.mode == "401":
            return httpx.Response(401, json={"message": "chave inválida"})
        if self.mode == "409":
            return httpx.Response(409, json={"message": "usuário não conectado"})
        if self.mode == "timeout":
            raise httpx.ReadTimeout("lento", request=request)
        if self.mode == "connect":
            raise httpx.ConnectError("sem rede", request=request)
        if self.mode == "not_json":
            return httpx.Response(200, text="<html>não é json</html>")
        if self.mode == "list":
            return httpx.Response(200, json=[1, 2, 3])
        if self.mode == "no_courses":
            return httpx.Response(200, json={"local_user_id": user_id})
        if path.endswith("/oauth/google/start"):
            if self.mode == "no_auth_url":
                return httpx.Response(200, json={"authorization_url": "http://inseguro"})
            return httpx.Response(200, json={"authorization_url": self.AUTH_URL})
        if path.endswith("/classroom/status"):
            return httpx.Response(200, json=self.statuses.get(user_id, {"connected": False, "status": "not_connected"}))
        if path.endswith("/classroom/courses"):
            return httpx.Response(200, json={"courses": self.courses.get(user_id, [])})
        if path.endswith("/classroom/sync"):
            return httpx.Response(200, json=self.sync_payload)
        if path.endswith("/classroom/connection"):
            self.disconnected.append(user_id)
            return httpx.Response(200, json={"disconnected": True})
        payload = self.exports.get(user_id, make_export(user_id, []))
        return httpx.Response(200, json=payload)

    def client(self) -> XanoClient:
        return XanoClient(
            base_url=TEST_BASE_URL, api_key=TEST_API_KEY, timeout=2.0,
            transport=httpx.MockTransport(self.handler),
        )

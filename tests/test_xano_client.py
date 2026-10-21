"""Testes do cliente Xano (httpx.MockTransport; nenhuma chamada de rede real)."""
import json
from datetime import datetime

import httpx
import pytest

from app.services.xano_client import (
    API_KEY_HEADER, XanoClient, XanoConfigError, XanoConnectionError, XanoError,
    XanoHTTPError, XanoInvalidResponseError, XanoTimeoutError,
)
from classroom_fakes import TEST_API_KEY, TEST_BASE_URL, FakeXano
from classroom_helpers import make_course, make_export


def test_get_export_envia_chave_e_usuario():
    fake = FakeXano()
    fake.exports[7] = make_export(7, [make_course()])
    data = fake.client().get_export(7)
    assert data["courses"][0]["google_course_id"] == "C1"
    request = fake.calls[0]
    assert request.method == "GET" and request.url.path.endswith("/classroom/export")
    assert request.url.params["local_user_id"] == "7"
    assert request.headers[API_KEY_HEADER] == TEST_API_KEY
    assert "since" not in request.url.params


def test_get_export_since_datetime_e_texto():
    fake = FakeXano()
    client = fake.client()
    client.get_export(1, since=datetime(2026, 10, 1, 12, 0, 0))
    client.get_export(1, since="2026-10-02T00:00:00Z")
    assert fake.calls[0].url.params["since"] == "2026-10-01T12:00:00"
    assert fake.calls[1].url.params["since"] == "2026-10-02T00:00:00Z"


def test_base_url_com_barra_final_nao_duplica():
    fake = FakeXano()
    client = XanoClient(base_url=TEST_BASE_URL + "/", api_key=TEST_API_KEY,
                        transport=httpx.MockTransport(fake.handler))
    client.get_export(1)
    assert "//classroom" not in str(fake.calls[0].url).replace("https://", "")


def test_status_cursos_e_start_sync():
    def handler(request):
        if request.url.path.endswith("/classroom/status"):
            return httpx.Response(200, json={"connected": True})
        if request.url.path.endswith("/classroom/courses"):
            return httpx.Response(200, json={"courses": [{"google_course_id": "C1"}]})
        if request.url.path.endswith("/classroom/sync"):
            assert request.method == "POST" and json.loads(request.content) == {"local_user_id": 3}
            return httpx.Response(200, json={"started": True})
        return httpx.Response(404)
    client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=httpx.MockTransport(handler))
    assert client.get_status(3) == {"connected": True}
    assert client.get_courses(3) == [{"google_course_id": "C1"}]
    assert client.start_sync(3) == {"started": True}


def test_get_courses_aceita_lista_pura():
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json=[{"google_course_id": "C1"}]))
    client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=transport)
    assert client.get_courses(1) == [{"google_course_id": "C1"}]


def test_configuracao_ausente_ou_invalida():
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={"courses": []}))
    for base, key in (("", TEST_API_KEY), ("   ", TEST_API_KEY), ("ftp://x", TEST_API_KEY), ("xano.test", TEST_API_KEY),
                      (TEST_BASE_URL, ""), (TEST_BASE_URL, "  ")):
        with pytest.raises(XanoConfigError):
            XanoClient(base_url=base, api_key=key, transport=transport).get_export(1)


def test_local_user_id_invalido():
    client = FakeXano().client()
    for bad in (0, -1, "1", None, True, 1.5):
        with pytest.raises(ValueError):
            client.get_export(bad)


def test_erros_http_viram_xano_http_error_sem_vazar_a_chave():
    for mode, status in (("500", 500), ("401", 401)):
        fake = FakeXano()
        fake.mode = mode
        with pytest.raises(XanoHTTPError) as info:
            fake.client().get_export(1)
        assert info.value.status_code == status
        assert TEST_API_KEY not in str(info.value) and TEST_API_KEY not in info.value.detail


def test_detalhe_do_erro_e_truncado():
    transport = httpx.MockTransport(lambda r: httpx.Response(502, text="x" * 5000))
    client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=transport)
    with pytest.raises(XanoHTTPError) as info:
        client.get_status(1)
    assert len(info.value.detail) <= 200


def test_timeout_e_falha_de_conexao():
    fake = FakeXano()
    fake.mode = "timeout"
    with pytest.raises(XanoTimeoutError):
        fake.client().get_export(1)
    fake.mode = "connect"
    with pytest.raises(XanoConnectionError):
        fake.client().get_export(1)


def test_respostas_invalidas():
    for mode in ("not_json", "list", "no_courses"):
        fake = FakeXano()
        fake.mode = mode
        with pytest.raises(XanoInvalidResponseError):
            fake.client().get_export(1)
    for body in ("texto", 5, {"x": 1}):  # cursos: precisa ser lista ou {"courses": [...]}
        transport = httpx.MockTransport(lambda r, b=body: httpx.Response(200, json=b))
        client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=transport)
        with pytest.raises(XanoInvalidResponseError):
            client.get_courses(1)
    for body in ("texto", 5, [1, 2]):  # status e sync: precisam ser objeto JSON
        transport = httpx.MockTransport(lambda r, b=body: httpx.Response(200, json=b))
        client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=transport)
        with pytest.raises(XanoInvalidResponseError):
            client.get_status(1)
        with pytest.raises(XanoInvalidResponseError):
            client.start_sync(1)


def test_todos_os_erros_herdam_de_xano_error():
    for exc in (XanoConfigError, XanoTimeoutError, XanoConnectionError, XanoHTTPError, XanoInvalidResponseError):
        assert issubclass(exc, XanoError)


def test_is_configured_nao_faz_requisicao():
    fake = FakeXano()
    assert fake.client().is_configured() is True
    for base, key in (("", TEST_API_KEY), ("ftp://x", TEST_API_KEY), (TEST_BASE_URL, ""), (TEST_BASE_URL, "  ")):
        assert XanoClient(base_url=base, api_key=key).is_configured() is False
    assert fake.calls == []


def test_start_oauth_devolve_url_https_do_xano():
    fake = FakeXano()
    url = fake.client().start_oauth(5, "http://localhost:8000/")
    assert url == FakeXano.AUTH_URL
    request = fake.calls[0]
    assert request.method == "POST" and request.url.path.endswith("/oauth/google/start")
    assert json.loads(request.content) == {"local_user_id": 5, "return_url": "http://localhost:8000/"}


def test_start_oauth_rejeita_resposta_sem_url_https():
    fake = FakeXano()
    fake.mode = "no_auth_url"
    with pytest.raises(XanoInvalidResponseError):
        fake.client().start_oauth(5, "http://localhost:8000/")
    for body in ({}, {"authorization_url": 5}, {"authorization_url": ""}, [1]):
        transport = httpx.MockTransport(lambda r, b=body: httpx.Response(200, json=b))
        client = XanoClient(base_url=TEST_BASE_URL, api_key=TEST_API_KEY, transport=transport)
        with pytest.raises(XanoInvalidResponseError):
            client.start_oauth(5, "http://localhost:8000/")


def test_disconnect():
    fake = FakeXano()
    assert fake.client().disconnect(9) == {"disconnected": True}
    assert fake.calls[0].method == "DELETE" and fake.disconnected == [9]
    fake.mode = "list"
    with pytest.raises(XanoInvalidResponseError):
        fake.client().disconnect(9)
    fake.mode = "409"
    with pytest.raises(XanoHTTPError) as info:
        fake.client().disconnect(9)
    assert info.value.status_code == 409

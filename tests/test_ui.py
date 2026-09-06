from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import app.main as main


@pytest.fixture
def client(monkeypatch):
    # Exercise application startup without paid APIs or a running Qdrant.
    service = Mock()
    service.ask.return_value = {
        "answer": "VPNクライアントを再起動してください。",
        "sources": [{"source": "faq/vpn-001", "title": "VPN", "score": 0.8}],
        "retrieval_ms": 12.0, "generation_ms": 34.0, "total_ms": 46.0,
    }
    monkeypatch.setattr(main, "RAGService", lambda: service)
    monkeypatch.setattr(main, "rag_service", None)
    with TestClient(main.app) as test_client:
        yield test_client, service


def test_ui_and_assets_are_served(client):
    http, _ = client
    response = http.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="ask-form"' in response.text
    for path in ("/static/app.js", "/static/style.css"):
        assert http.get(path).status_code == 200


def test_ui_request_reaches_rag_and_returns_metrics(client):
    http, service = client
    response = http.post("/ask", json={"question": "VPN?", "top_k": 5})
    assert response.status_code == 200
    service.ask.assert_called_once_with("VPN?", 5)
    assert response.json()["sources"][0]["source"] == "faq/vpn-001"
    assert response.json()["total_ms"] == 46.0


@pytest.mark.parametrize("payload", [
    {"question": "", "top_k": 3},
    {"question": "test", "top_k": 0},
    {"question": "test", "top_k": 11},
    {"question": "x" * 2001, "top_k": 3},
])
def test_invalid_requests_do_not_call_rag(client, payload):
    http, service = client
    assert http.post("/ask", json=payload).status_code == 422
    service.ask.assert_not_called()


def test_service_failure_returns_error(client):
    http, service = client
    service.ask.side_effect = RuntimeError("test failure")
    assert http.post("/ask", json={"question": "VPN?"}).status_code == 500

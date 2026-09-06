from fastapi.testclient import TestClient

from app.main import app


def test_health():
    # startup時に外部サービスへ接続しないよう、
    # lifespanを起動せずルート関数の基本レスポンスを確認する。
    route = next(r for r in app.routes if getattr(r, "path", None) == "/health")
    assert route.endpoint() == {"status": "ok"}

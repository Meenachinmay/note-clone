import os

from fastapi.testclient import TestClient


def test_health_check_returns_ok(monkeypatch=None):
    # Ensure we use the test config which disables DB attempts on import/startup
    os.environ["APP_ENVIRONMENT"] = "test"

    # Import here so that it reads the APP_ENVIRONMENT we just set
    from src.main import app

    client = TestClient(app)
    resp = client.get("/health-check")
    assert resp.status_code == 200
    assert resp.text == "ok"

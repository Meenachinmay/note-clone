import os

from fastapi.testclient import TestClient


def _get_client() -> TestClient:
    # Ensure test env
    os.environ["APP_ENVIRONMENT"] = "test"
    from src.main import app
    return TestClient(app)


def _signup_and_get_token(client: TestClient, email: str, password: str) -> str:
    r = client.post("/auth/signup", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_logout_success_and_token_revoked_for_subsequent_requests():
    client = _get_client()
    token = _signup_and_get_token(client, "logoutuser@example.com", "SuperSecret123")

    # First logout succeeds
    r1 = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 200, r1.text
    assert r1.json() == {"success": True}

    # Second attempt with same token should now be rejected by middleware
    r2 = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 401
    assert r2.json().get("detail") in ("Session revoked", "Invalid token")


def test_logout_without_authorization_header_returns_401():
    client = _get_client()
    r = client.post("/auth/logout")
    assert r.status_code == 401
    assert r.json().get("detail") in ("Not authenticated",)

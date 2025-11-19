import os

from fastapi.testclient import TestClient


def _get_client() -> TestClient:
    # Ensure test env
    os.environ["APP_ENVIRONMENT"] = "test"
    from src.main import app
    return TestClient(app)


def test_signup_success_creates_user_and_returns_token():
    client = _get_client()
    payload = {"email": "newuser@example.com", "password": "StrongPass123"}

    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert "access_token" in body and isinstance(body["access_token"], str)
    assert body.get("token_type") == "bearer"
    assert "user" in body and isinstance(body["user"], dict)
    assert body["user"]["email"] == payload["email"].lower()
    assert isinstance(body["user"]["id"], int)

    # Verify user persisted and password hashed
    from src.infrastructure.repositories.users_repository import get_user_by_email
    from src.infrastructure.security.password import verify_password

    user = get_user_by_email(payload["email"].lower())
    assert user is not None
    assert user["email"] == payload["email"].lower()
    assert user["password_hash"] != payload["password"]
    assert verify_password(payload["password"], user["password_hash"]) is True


def test_signup_duplicate_email_returns_400():
    client = _get_client()
    payload = {"email": "dupe@example.com", "password": "AnotherPass123"}

    first = client.post("/auth/signup", json=payload)
    assert first.status_code == 200

    second = client.post("/auth/signup", json=payload)
    assert second.status_code == 400
    body = second.json()
    assert body.get("detail") in ("Email already registered", "Invalid email")


def test_signup_invalid_email_returns_400():
    client = _get_client()
    payload = {"email": "invalid-email", "password": "ValidPass123"}

    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 400
    assert resp.json().get("detail") == "Invalid email"


def test_signup_short_password_returns_400():
    client = _get_client()
    payload = {"email": "shortpass@example.com", "password": "short"}

    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 400
    assert (
        resp.json().get("detail")
        == "Password must be at least 8 characters long"
    )

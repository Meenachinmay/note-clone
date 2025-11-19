import os

from fastapi.testclient import TestClient


def _get_client() -> TestClient:
    # Ensure test env
    os.environ["APP_ENVIRONMENT"] = "test"
    from src.main import app
    return TestClient(app)


def test_login_success_after_signup_returns_token_and_user():
    client = _get_client()
    payload = {"email": "loginuser@example.com", "password": "StrongPass123"}

    # Create user via signup
    r_signup = client.post("/auth/signup", json=payload)
    assert r_signup.status_code == 200, r_signup.text

    # Login with same credentials
    r_login = client.post("/auth/login", json=payload)
    assert r_login.status_code == 200, r_login.text
    body = r_login.json()
    assert "access_token" in body and isinstance(body["access_token"], str)
    assert body.get("token_type") == "bearer"
    assert body.get("user", {}).get("email") == payload["email"].lower()


def test_login_wrong_password_returns_401():
    client = _get_client()
    email = "wrongpass@example.com"
    # Create user
    r_signup = client.post("/auth/signup", json={"email": email, "password": "CorrectPass123"})
    assert r_signup.status_code == 200

    # Attempt login with wrong password
    r_login = client.post("/auth/login", json={"email": email, "password": "Incorrect999"})
    assert r_login.status_code == 401
    assert r_login.json().get("detail") in ("Invalid credentials",)


def test_login_non_existent_email_returns_401():
    client = _get_client()
    r_login = client.post(
        "/auth/login", json={"email": "doesnotexist@example.com", "password": "SomePass123"}
    )
    assert r_login.status_code == 401
    assert r_login.json().get("detail") in ("Invalid credentials",)


def test_login_invalid_email_returns_400():
    client = _get_client()
    r_login = client.post(
        "/auth/login", json={"email": "not-an-email", "password": "SomePass123"}
    )
    assert r_login.status_code == 400
    assert r_login.json().get("detail") == "Invalid email"


def test_login_short_password_returns_400():
    client = _get_client()
    r_login = client.post(
        "/auth/login", json={"email": "user@example.com", "password": "short"}
    )
    assert r_login.status_code == 400
    assert (
        r_login.json().get("detail")
        == "Password must be at least 8 characters long"
    )

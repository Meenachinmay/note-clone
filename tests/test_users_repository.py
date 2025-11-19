import os


def _ensure_test_env():
    os.environ["APP_ENVIRONMENT"] = "test"


def test_create_and_read_user_by_email_and_id():
    _ensure_test_env()
    from src.infrastructure.repositories.users_repository import (
        create_user,
        get_user_by_email,
        get_user_by_id,
    )

    email = "repo_user1@example.com"
    pwd_hash = "hashed:dummy"

    # Create
    user = create_user(email=email, password_hash=pwd_hash)
    assert user["email"] == email
    assert isinstance(user["id"], int)
    assert user["password_hash"] == pwd_hash
    assert user["created_at"] is not None

    # Read by email
    by_email = get_user_by_email(email)
    assert by_email is not None
    assert by_email["id"] == user["id"]
    assert by_email["email"] == email

    # Read by id
    by_id = get_user_by_id(user["id"])
    assert by_id is not None
    assert by_id["email"] == email


def test_create_user_duplicate_email_raises_value_error():
    _ensure_test_env()
    from src.infrastructure.repositories.users_repository import create_user

    email = "repo_duplicate@example.com"
    pwd_hash = "hash1"
    user = create_user(email=email, password_hash=pwd_hash)
    assert user["email"] == email

    try:
        create_user(email=email, password_hash="hash2")
        assert False, "Expected ValueError for duplicate email"
    except ValueError as e:
        assert str(e) == "Email already registered"

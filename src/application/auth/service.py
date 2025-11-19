import re
from typing import Dict, Any

from src.infrastructure.repositories import users_repository as users_repo
from src.infrastructure.repositories import sessions_repository as sessions_repo
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.security.jwt import create_access_token


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(email: str) -> None:
    if not email or not _EMAIL_RE.match(email):
        raise ValueError("Invalid email")


def _validate_password(password: str) -> None:
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")


def signup(email: str, password: str) -> Dict[str, Any]:
    _validate_email(email)
    _validate_password(password)

    pwd_hash = hash_password(password)
    try:
        user = users_repo.create_user(email=email.lower().strip(), password_hash=pwd_hash)
    except ValueError as e:
        # Email already exists
        raise e

    token_info = create_access_token(sub=str(user["id"]))
    sessions_repo.create_session(user_id=user["id"], jti=token_info["jti"])
    return {
        "access_token": token_info["token"],
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"]},
    }


def login(email: str, password: str) -> Dict[str, Any]:
    _validate_email(email)
    _validate_password(password)

    user = users_repo.get_user_by_email(email.lower().strip())
    if not user:
        raise PermissionError("Invalid credentials")
    if not verify_password(password, user["password_hash"]):
        raise PermissionError("Invalid credentials")

    token_info = create_access_token(sub=str(user["id"]))
    sessions_repo.create_session(user_id=user["id"], jti=token_info["jti"])
    return {
        "access_token": token_info["token"],
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"]},
    }


def logout(jti: str) -> bool:
    if not jti:
        return False
    return sessions_repo.revoke_session(jti)

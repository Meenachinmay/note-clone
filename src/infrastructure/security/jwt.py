import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt

from src.config import config


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(sub: str, extra_claims: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    jwt_cfg = config.get("jwt", {})
    secret = jwt_cfg["secret"]
    algorithm = jwt_cfg.get("algorithm", "HS256")
    issuer = jwt_cfg.get("issuer", "note-clone")
    audience = jwt_cfg.get("audience", "note-clone-users")
    ttl_minutes = int(jwt_cfg.get("access_token_ttl_minutes", 60))

    jti = uuid.uuid4().hex
    now = _now()
    payload: Dict[str, Any] = {
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
        "sub": sub,
        "jti": jti,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, secret, algorithm=algorithm)
    return {"token": token, "jti": jti}


def decode_and_verify_token(token: str) -> Dict[str, Any]:
    jwt_cfg = config.get("jwt", {})
    secret = jwt_cfg["secret"]
    algorithm = jwt_cfg.get("algorithm", "HS256")
    issuer = jwt_cfg.get("issuer", "note-clone")
    audience = jwt_cfg.get("audience", "note-clone-users")

    return jwt.decode(
        token,
        secret,
        algorithms=[algorithm],
        audience=audience,
        issuer=issuer,
    )

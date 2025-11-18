from typing import Callable, Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

# Lazy import heavy dependencies inside the request cycle to avoid import-time
# errors in environments where optional deps aren't installed (e.g., tests).


PUBLIC_PATHS: Iterable[str] = (
    "/health-check",
    "/auth/login",
    "/auth/signup",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if request.method == "OPTIONS" or any(
            path == p or path.startswith(p + "/") for p in PUBLIC_PATHS
        ):
            return await call_next(request)

        # Expect Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth_header.split(" ", 1)[1].strip()
        try:
            from src.infrastructure.security.jwt import decode_and_verify_token
            claims = decode_and_verify_token(token)
        except Exception:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        jti = claims.get("jti")
        sub = claims.get("sub")
        if not jti or not sub:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        # Verify session is active
        from src.infrastructure.repositories.sessions_repository import is_session_active
        if not is_session_active(jti):
            return JSONResponse({"detail": "Session revoked"}, status_code=401)

        # Load user
        try:
            user_id = int(sub)
        except (TypeError, ValueError):
            return JSONResponse({"detail": "Invalid subject"}, status_code=401)

        from src.infrastructure.repositories.users_repository import get_user_by_id
        user = get_user_by_id(user_id)
        if not user:
            return JSONResponse({"detail": "User not found"}, status_code=401)

        # Attach user context
        request.state.user = {"id": user["id"], "email": user["email"]}
        request.state.token_claims = claims
        return await call_next(request)

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from src.application.auth import service as auth_service


class Credentials(BaseModel):
    email: str
    password: str


auth_router = APIRouter()


@auth_router.post("/signup")
def signup(payload: Credentials):
    try:
        result = auth_service.signup(email=payload.email, password=payload.password)
        return result
    except ValueError as e:
        # Invalid input or email already registered
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@auth_router.post("/login")
def login(payload: Credentials):
    try:
        result = auth_service.login(email=payload.email, password=payload.password)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except ValueError as e:
        # invalid email/password format
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@auth_router.post("/logout")
def logout(request: Request):
    claims = getattr(request.state, "token_claims", None)
    if not claims or "jti" not in claims:
        # Shouldn't happen if middleware works, but guard anyway
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    ok = auth_service.logout(jti=claims["jti"]) 
    if not ok:
        # Already revoked or not found
        return {"success": False}
    return {"success": True}

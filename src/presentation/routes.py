from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.application.health_check_handler import HealthCheckHandler


router = APIRouter()
_health_handler = HealthCheckHandler()


@router.get("/health-check", response_class=PlainTextResponse)
def health_check():
    # Return plain text "ok" with 200 status code
    return _health_handler.handle()

from fastapi import FastAPI
from src.config import config, ENV_NAME
from src.logging_config import logger
from src.infrastructure.database.connection import get_db_connection
from src.presentation.routes import router
from src.presentation.auth_routes import auth_router
from src.presentation.auth_middleware import AuthMiddleware
from src.infrastructure.database.migrations import run_migrations

app = FastAPI()
app.add_middleware(AuthMiddleware)

@app.on_event("startup")
async def startup_event():
    # Required startup logs
    logger.info(f"loading config for {ENV_NAME}")
    # Optionally check DB connectivity once at startup and close immediately to avoid leaking connections
    if config.get('database', {}).get('enabled', True):
        conn = get_db_connection()
        try:
            # Run DB migrations at startup
            run_migrations(conn)
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
    logger.info(f"starting server on port:{config['server']['port']} number")

app.include_router(router)
app.include_router(auth_router, prefix="/auth", tags=["auth"])

from fastapi import FastAPI
from src.config import config, ENV_NAME
from src.logging_config import logger
from src.infrastructure.database.connection import get_db_connection
from src.presentation.routes import router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Required startup logs
    logger.info(f"loading config for {ENV_NAME}")
    # Optionally check DB connectivity once at startup and close immediately to avoid leaking connections
    if config.get('database', {}).get('enabled', True):
        conn = get_db_connection()
        try:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
    logger.info(f"starting server on port:{config['server']['port']} number")

app.include_router(router)

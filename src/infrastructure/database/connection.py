import time
import psycopg2
from src.config import config
from src.logging_config import logger

def get_db_connection(max_retries: int = 10, delay_seconds: float = 1.0):
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            # Required log format
            logger.info("connecting database connection")
            conn = psycopg2.connect(
                host=config['database']['host'],
                port=config['database']['port'],
                user=config['database']['user'],
                password=config['database']['password'],
                dbname=config['database']['dbname']
            )
            logger.info("Database connection successful.")
            return conn
        except psycopg2.OperationalError as e:
            last_exc = e
            logger.warning(f"Database connection failed (attempt {attempt}/{max_retries}): {e}")
            time.sleep(delay_seconds)
    logger.error(f"Could not connect to the database after {max_retries} attempts: {last_exc}")
    raise last_exc

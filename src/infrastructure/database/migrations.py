from typing import List, Tuple
import psycopg2
from psycopg2.extensions import connection as PgConnection
from src.logging_config import logger


# Each migration is a tuple of (version, up_sql)
MIGRATIONS: List[Tuple[str, str]] = [
    (
        "0001_create_auth",
        """
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            email VARCHAR(320) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS auth_sessions (
            jti VARCHAR(64) PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            revoked_at TIMESTAMPTZ NULL
        );

        CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);
        """
    ),
]


def _ensure_schema_migrations_table(conn: PgConnection):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(100) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        conn.commit()


def run_migrations(conn: PgConnection):
    """Run pending migrations within the given connection.
    This function is idempotent and safe to call at startup.
    """
    logger.info("Running database migrations (if any)")
    _ensure_schema_migrations_table(conn)

    applied = set()
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations")
        rows = cur.fetchall()
        applied = {r[0] for r in rows}

    for version, sql in MIGRATIONS:
        if version in applied:
            continue
        logger.info(f"Applying migration {version}")
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    cur.execute(
                        "INSERT INTO schema_migrations(version) VALUES (%s)", (version,)
                    )
            logger.info(f"Migration {version} applied")
        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            raise

import os
from typing import Generator

import psycopg2
from psycopg2 import sql
import pytest


def _provision_test_database() -> None:
    # Ensure tests use the test config
    os.environ["APP_ENVIRONMENT"] = "test"

    # Import config after setting environment
    from src.config import config as app_config

    db_cfg = app_config["database"]
    host = db_cfg["host"]
    port = db_cfg["port"]
    user = db_cfg["user"]
    password = db_cfg["password"]
    dbname = db_cfg["dbname"]

    # Connect to the server using a maintenance DB (postgres) to manage databases
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
    try:
        conn.autocommit = True  # Required for DROP/CREATE DATABASE
        with conn.cursor() as cur:
            # Terminate any existing connections to the test DB (defensive)
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                (dbname,),
            )
            # Drop and recreate the test database
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {};").format(sql.Identifier(dbname)))
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {};").format(
                    sql.Identifier(dbname), sql.Identifier(user)
                )
            )
    finally:
        conn.close()

    # Connect to the freshly created test DB and run migrations explicitly
    # This avoids relying on app startup for schema setup.
    from src.infrastructure.database.migrations import run_migrations
    test_conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
    try:
        run_migrations(test_conn)
    finally:
        test_conn.close()


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db() -> Generator[None, None, None]:
    """Session-wide auto fixture to prepare a clean test database.
    - Sets APP_ENVIRONMENT=test
    - Drops and recreates the configured test database
    Migrations will be applied by the app on startup.
    """
    _provision_test_database()
    yield
    # Always clean up the test database after the test session
    # Ensure we are still targeting test environment
    os.environ["APP_ENVIRONMENT"] = "test"
    from src.config import config as app_config
    dbname = app_config["database"]["dbname"]
    host = app_config["database"]["host"]
    port = app_config["database"]["port"]
    user = app_config["database"]["user"]
    password = app_config["database"]["password"]

    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            # Terminate any remaining connections to the test DB to allow dropping
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                (dbname,),
            )
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {};").format(sql.Identifier(dbname)))
    finally:
        conn.close()

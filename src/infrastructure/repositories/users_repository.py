from typing import Optional, Dict, Any

import psycopg2

from src.infrastructure.database.connection import get_db_connection


def _row_to_user(row) -> Dict[str, Any]:
    return {
        "id": row[0],
        "email": row[1],
        "password_hash": row[2],
        "created_at": row[3],
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = %s",
                (email,),
            )
            row = cur.fetchone()
            return _row_to_user(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return _row_to_user(row) if row else None
    finally:
        conn.close()


def create_user(email: str, password_hash: str) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash)
                    VALUES (%s, %s)
                    RETURNING id, email, password_hash, created_at
                    """,
                    (email, password_hash),
                )
                row = cur.fetchone()
                return _row_to_user(row)
    except psycopg2.Error as e:
        # Unique violation for email
        if getattr(e, "pgcode", None) == "23505":
            raise ValueError("Email already registered") from e
        raise
    finally:
        conn.close()

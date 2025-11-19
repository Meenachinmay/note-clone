from typing import Optional

from src.infrastructure.database.connection import get_db_connection


def create_session(user_id: int, jti: str) -> None:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO auth_sessions (jti, user_id) VALUES (%s, %s)",
                    (jti, user_id),
                )
    finally:
        conn.close()


def is_session_active(jti: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT revoked_at IS NULL FROM auth_sessions WHERE jti = %s",
                (jti,),
            )
            row = cur.fetchone()
            if not row:
                return False
            return bool(row[0])
    finally:
        conn.close()


def revoke_session(jti: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE auth_sessions SET revoked_at = NOW() WHERE jti = %s AND revoked_at IS NULL",
                    (jti,),
                )
                return cur.rowcount > 0
    finally:
        conn.close()

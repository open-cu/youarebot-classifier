import psycopg2
from psycopg2.extensions import connection as _connection
from typing import List, Dict

from .config import DB_URL


def get_db_connection() -> _connection:
    return psycopg2.connect(DB_URL)


def init_db() -> None:
    """
    create database and table`messages`.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY,
                    text TEXT NOT NULL,
                    dialog_id UUID NOT NULL,
                    participant_index INT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    finally:
        conn.close()


def insert_message(
        id,  # UUID
        text: str,
        dialog_id,  # UUID
        participant_index: int
) -> None:
    """
    stores one message in db
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (id, text, dialog_id, participant_index)
                VALUES (%s, %s, %s, %s);
                """,
                (str(id), text, str(dialog_id), participant_index)
            )
        conn.commit()
    finally:
        conn.close()


def select_messages_by_dialog(dialog_id) -> List[Dict[str, str]]:
    """
    returns list of messages for current dialog_id ordered by time
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT text, participant_index
                FROM messages
                WHERE dialog_id = %s
                ORDER BY created_at ASC;
                """,
                (str(dialog_id),)
            )
            rows = cur.fetchall()
        return [
            {"text": row[0], "participant_index": row[1]}
            for row in rows
        ]
    finally:
        conn.close()

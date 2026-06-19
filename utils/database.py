from pathlib import Path
import os
import sqlite3
from typing import List, Optional, Tuple

# Allow overriding DB path via env (Railway persistent volume e.g. /data/avatar.db)
DB_PATH = os.getenv("DB_PATH", "data/avatar.db")

# If DB_PATH is a plain filesystem path, ensure its parent exists
_using_uri = DB_PATH.startswith("file:") or DB_PATH.startswith("sqlite:")
if not _using_uri:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Build SQLite URI with shared cache for slightly better concurrency when using a mounted volume
if _using_uri:
    _uri = DB_PATH
else:
    # file:/absolute/path or relative paths both work
    _uri = f"file:{DB_PATH}?cache=shared"

conn = sqlite3.connect(_uri, uri=True, check_same_thread=False, timeout=30)
cursor = conn.cursor()

# Recommended PRAGMAs for durability and concurrent reads
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")
cursor.execute("PRAGMA foreign_keys=ON;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS avatar_schedule (
    guild_id INTEGER PRIMARY KEY,
    member_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    interval_minutes INTEGER NOT NULL,
    last_sent INTEGER NOT NULL DEFAULT 0
)
""")
conn.commit()


def save_config(
    guild_id: int,
    member_id: int,
    channel_id: int,
    interval_minutes: int,
) -> None:
    """Insert or update a guild schedule. Preserves last_sent when updating."""
    cursor.execute(
        """
        INSERT OR REPLACE INTO avatar_schedule (
            guild_id,
            member_id,
            channel_id,
            interval_minutes,
            last_sent
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            COALESCE(
                (
                    SELECT last_sent
                    FROM avatar_schedule
                    WHERE guild_id = ?
                ),
                0
            )
        )
        """,
        (
            int(guild_id),
            int(member_id),
            int(channel_id),
            int(interval_minutes),
            int(guild_id),
        ),
    )
    conn.commit()


def get_config(guild_id: int) -> Optional[Tuple[int, int, int, int, int]]:
    cursor.execute(
        """
        SELECT guild_id, member_id, channel_id, interval_minutes, last_sent
        FROM avatar_schedule
        WHERE guild_id = ?
        """,
        (int(guild_id),),
    )
    return cursor.fetchone()


def get_all_configs() -> List[Tuple[int, int, int, int, int]]:
    cursor.execute(
        """
        SELECT guild_id, member_id, channel_id, interval_minutes, last_sent
        FROM avatar_schedule
        """
    )
    return cursor.fetchall()


def update_last_sent(guild_id: int, timestamp: int) -> None:
    cursor.execute(
        """
        UPDATE avatar_schedule
        SET last_sent = ?
        WHERE guild_id = ?
        """,
        (int(timestamp), int(guild_id)),
    )
    conn.commit()


def remove_config(guild_id: int) -> None:
    cursor.execute(
        """
        DELETE FROM avatar_schedule
        WHERE guild_id = ?
        """,
        (int(guild_id),),
    )
    conn.commit()

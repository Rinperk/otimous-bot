import sqlite3

conn = sqlite3.connect(
    "avatar.db",
    check_same_thread=False
)

cursor = conn.cursor()

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
    interval_minutes: int
):
    cursor.execute("""
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
    """, (
        guild_id,
        member_id,
        channel_id,
        interval_minutes,
        guild_id
    ))

    conn.commit()

def get_config(guild_id: int):
    cursor.execute("""
    SELECT *
    FROM avatar_schedule
    WHERE guild_id = ?
    """, (guild_id,))

    return cursor.fetchone()

def get_all_configs():
    cursor.execute("""
    SELECT *
    FROM avatar_schedule
    """)

    return cursor.fetchall()

def update_last_sent(
    guild_id: int,
    timestamp: int
):
    cursor.execute("""
    UPDATE avatar_schedule
    SET last_sent = ?
    WHERE guild_id = ?
    """, (
        timestamp,
        guild_id
    ))

    conn.commit()

def remove_config(guild_id: int):
    cursor.execute("""
    DELETE FROM avatar_schedule
    WHERE guild_id = ?
    """, (guild_id,))

    conn.commit()
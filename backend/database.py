import sqlite3, pathlib

DB_PATH = pathlib.Path(__file__).parent / "mindbridge.db"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS moods (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            mood        INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 5),
            label       TEXT    NOT NULL,
            emoji       TEXT    NOT NULL,
            note        TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('user','ai')),
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS community_posts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            content     TEXT    NOT NULL,
            tag         TEXT    DEFAULT 'General',
            upvotes     INTEGER DEFAULT 0,
            created_at  TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS post_votes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id     INTEGER NOT NULL,
            session_id  TEXT    NOT NULL,
            UNIQUE(post_id, session_id)
        );

        CREATE INDEX IF NOT EXISTS idx_moods_session   ON moods(session_id);
        CREATE INDEX IF NOT EXISTS idx_chat_session    ON chat_messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_posts_created   ON community_posts(created_at DESC);
    """)
    db.commit()
    db.close()
    print(f"✅ Database ready at {DB_PATH}")

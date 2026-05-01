"""SQLite-backed conversation store. Zero-config, persistent, swappable."""
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from src.tools.interfaces import ConversationStore

_DEFAULT_DB = Path(__file__).parent.parent.parent.parent / "data" / "conversations.db"


class SQLiteConversationStore(ConversationStore):
    def __init__(self, config: dict | None = None):
        db_path = (config or {}).get("db_path", str(_DEFAULT_DB))
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(str(self._db_path))
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self):
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT 'New chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                agent TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        """)
        conn.commit()

    def _ensure_session(self, session_id: str):
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, "New chat", now, now),
        )
        conn.commit()

    def save_message(self, session_id: str, role: str, content: str, agent: str = "") -> None:
        self._ensure_session(session_id)
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO messages (session_id, role, content, agent, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, agent, now),
        )
        conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        msg_count = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ? AND role = 'user'", (session_id,)
        ).fetchone()[0]
        if msg_count == 1 and role == "user":
            title = content[:60].strip()
            if len(content) > 60:
                title += "..."
            conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        conn.commit()

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT role, content, agent, timestamp FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def list_sessions(self) -> list[dict]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_session_title(self, session_id: str) -> str:
        conn = self._conn()
        row = conn.execute("SELECT title FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return row["title"] if row else "New chat"

    def set_session_title(self, session_id: str, title: str) -> None:
        conn = self._conn()
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        conn.commit()

    def delete_session(self, session_id: str) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()

    def clear_session(self, session_id: str) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()

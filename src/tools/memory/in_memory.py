"""In-memory conversation store for development."""
from datetime import datetime, timezone

from src.tools.interfaces import ConversationStore

_STORE: dict[str, list[dict]] = {}
_TITLES: dict[str, str] = {}


class InMemoryConversationStore(ConversationStore):
    def save_message(self, session_id: str, role: str, content: str, agent: str = "") -> None:
        _STORE.setdefault(session_id, []).append({
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        return _STORE.get(session_id, [])[-limit:]

    def list_sessions(self) -> list[dict]:
        sessions = []
        for sid, msgs in _STORE.items():
            if msgs:
                sessions.append({
                    "id": sid,
                    "title": _TITLES.get(sid, msgs[0].get("content", "New chat")[:50]),
                    "updated_at": msgs[-1].get("timestamp", ""),
                })
        return sorted(sessions, key=lambda s: s["updated_at"], reverse=True)

    def get_session_title(self, session_id: str) -> str:
        return _TITLES.get(session_id, "New chat")

    def set_session_title(self, session_id: str, title: str) -> None:
        _TITLES[session_id] = title

    def delete_session(self, session_id: str) -> None:
        _STORE.pop(session_id, None)
        _TITLES.pop(session_id, None)

    def clear_session(self, session_id: str) -> None:
        _STORE.pop(session_id, None)

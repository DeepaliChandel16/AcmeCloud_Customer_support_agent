"""Conversation memory store factory."""
from src.tools.interfaces import ConversationStore


def get_conversation_store(config: dict) -> ConversationStore:
    provider = config.get("provider", "sqlite")
    if provider == "redis":
        from src.tools.memory.redis_store import RedisConversationStore
        return RedisConversationStore(config)
    elif provider == "sqlite":
        from src.tools.memory.sqlite_store import SQLiteConversationStore
        return SQLiteConversationStore(config)
    elif provider == "memory":
        from src.tools.memory.in_memory import InMemoryConversationStore
        return InMemoryConversationStore()
    else:
        raise ValueError(f"Unknown conversation store provider: {provider}")

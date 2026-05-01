"""Redis conversation store stub.

To activate: set integrations.conversation_store.provider = "redis" in settings.yaml
and provide REDIS_URL env var.

Implementation notes:
- Uses redis-py: pip install redis
- Key schema: conversation:{session_id} -> JSON list of messages
- TTL: configurable per session (e.g., 24 hours)
- For production: use Redis Streams or sorted sets for ordering
"""
import os

from src.tools.interfaces import ConversationStore


class RedisConversationStore(ConversationStore):
    def __init__(self, config: dict):
        self.redis_url = os.getenv("REDIS_URL", config.get("redis_url", "redis://localhost:6379"))
        self.ttl = config.get("ttl_seconds", 86400)

    def save_message(self, session_id: str, role: str, content: str, agent: str = "") -> None:
        # TODO: redis.rpush(f"conversation:{session_id}", json.dumps({...}))
        # TODO: redis.expire(f"conversation:{session_id}", self.ttl)
        raise NotImplementedError("Redis save_message not yet implemented.")

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        # TODO: redis.lrange(f"conversation:{session_id}", -limit, -1)
        raise NotImplementedError("Redis get_history not yet implemented.")

    def clear_session(self, session_id: str) -> None:
        # TODO: redis.delete(f"conversation:{session_id}")
        raise NotImplementedError("Redis clear_session not yet implemented.")

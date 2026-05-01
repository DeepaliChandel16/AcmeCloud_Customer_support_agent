"""Patched Ollama client that filters unsupported options."""
from collections.abc import Mapping, Sequence
from typing import Any, override

from agent_framework._types import Message
from agent_framework.ollama import OllamaChatClient

UNSUPPORTED_OPTIONS = {"allow_multiple_tool_calls", "conversation_id", "store"}


class PatchedOllamaChatClient(OllamaChatClient):
    @override
    def _prepare_options(self, messages: Sequence[Message], options: Mapping[str, Any]) -> dict[str, Any]:
        filtered = {k: v for k, v in options.items() if k not in UNSUPPORTED_OPTIONS}
        return super()._prepare_options(messages, filtered)

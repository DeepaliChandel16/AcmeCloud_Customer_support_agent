from agent_framework import Agent

from src.config import AppConfig
from src.tools.registry import ToolRegistry


def create_account_agent(client, config: AppConfig, registry: ToolRegistry) -> Agent:
    agent_cfg = config.agents["account"]
    return client.as_agent(
        name=agent_cfg.name,
        instructions=agent_cfg.instructions,
        description=agent_cfg.description,
        tools=registry.account_tools(),
        require_per_service_call_history_persistence=True,
    )

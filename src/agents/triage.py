from agent_framework import Agent

from src.config import AppConfig


def create_triage_agent(client, config: AppConfig) -> Agent:
    agent_cfg = config.agents["triage"]
    return client.as_agent(
        name=agent_cfg.name,
        instructions=agent_cfg.instructions,
        description=agent_cfg.description,
        require_per_service_call_history_persistence=True,
    )

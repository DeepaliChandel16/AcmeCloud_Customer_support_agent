import logging

from agent_framework.orchestrations import HandoffBuilder

from src.agents.triage import create_triage_agent
from src.agents.knowledge import create_knowledge_agent
from src.agents.account import create_account_agent
from src.agents.billing import create_billing_agent
from src.agents.ticket import create_ticket_agent
from src.clients import PatchedOllamaChatClient
from src.config import AppConfig
from src.tools.registry import ToolRegistry

logger = logging.getLogger("acmecloud.workflow")


def build_support_workflow(config: AppConfig):
    logger.info("Building workflow (model=%s, host=%s)", config.ollama.model, config.ollama.host)
    client = PatchedOllamaChatClient(host=config.ollama.host, model=config.ollama.model)
    registry = ToolRegistry(config)

    triage = create_triage_agent(client, config)
    knowledge = create_knowledge_agent(client, config, registry)
    account = create_account_agent(client, config, registry)
    billing = create_billing_agent(client, config, registry)
    ticket = create_ticket_agent(client, config, registry)
    logger.info("Agents created: triage, knowledge, account, billing, ticket")

    workflow = (
        HandoffBuilder(
            name="acmecloud_support",
            participants=[triage, knowledge, account, billing, ticket],
        )
        .with_start_agent(triage)
        .add_handoff(triage, [knowledge, account, billing, ticket])
        .add_handoff(knowledge, [triage])
        .add_handoff(account, [triage])
        .add_handoff(billing, [triage])
        .add_handoff(ticket, [triage])
        .build()
    )
    logger.info("Handoff workflow built successfully")

    return workflow

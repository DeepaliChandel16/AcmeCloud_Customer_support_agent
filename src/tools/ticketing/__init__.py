"""Ticketing tool factory. Returns the right provider based on config."""
from src.tools.interfaces import TicketingProvider


def get_ticketing_provider(config: dict) -> TicketingProvider:
    provider = config.get("provider", "mock")
    if provider == "zendesk":
        from src.tools.ticketing.zendesk import ZendeskTicketing
        return ZendeskTicketing(config)
    elif provider == "mock":
        from src.tools.ticketing.mock import MockTicketing
        return MockTicketing()
    else:
        raise ValueError(f"Unknown ticketing provider: {provider}")

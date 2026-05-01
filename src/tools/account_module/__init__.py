"""Account tool factory."""
from src.tools.interfaces import AccountProvider


def get_account_provider(config: dict) -> AccountProvider:
    provider = config.get("provider", "mock")
    if provider == "entra":
        from src.tools.account_module.entra import EntraAccount
        return EntraAccount(config)
    elif provider == "mock":
        from src.tools.account_module.mock import MockAccount
        return MockAccount()
    else:
        raise ValueError(f"Unknown account provider: {provider}")

"""CRM tool factory."""
from src.tools.interfaces import CRMProvider


def get_crm_provider(config: dict) -> CRMProvider:
    provider = config.get("provider", "mock")
    if provider == "salesforce":
        from src.tools.crm_module.salesforce import SalesforceCRM
        return SalesforceCRM(config)
    elif provider == "mock":
        from src.tools.crm_module.mock import MockCRM
        return MockCRM()
    else:
        raise ValueError(f"Unknown CRM provider: {provider}")

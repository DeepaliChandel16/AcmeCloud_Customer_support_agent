"""Billing tool factory."""
from src.tools.interfaces import BillingProvider


def get_billing_provider(config: dict) -> BillingProvider:
    provider = config.get("provider", "mock")
    if provider == "stripe":
        from src.tools.billing_module.stripe_billing import StripeBilling
        return StripeBilling(config)
    elif provider == "mock":
        from src.tools.billing_module.mock import MockBilling
        return MockBilling()
    else:
        raise ValueError(f"Unknown billing provider: {provider}")

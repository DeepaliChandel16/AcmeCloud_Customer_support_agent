"""Stripe billing provider stub.

To activate: set integrations.billing.provider = "stripe" in settings.yaml
and provide STRIPE_API_KEY env var.

Implementation notes:
- Uses Stripe Python SDK: pip install stripe
- Invoices: stripe.Invoice.retrieve(invoice_id)
- Refunds: stripe.Refund.create(charge=charge_id, reason=reason)
- Cancel subscription: stripe.Subscription.modify(sub_id, cancel_at_period_end=True)
- Webhook: listen for invoice.payment_failed, customer.subscription.deleted events
"""
import os

from src.tools.interfaces import BillingProvider


class StripeBilling(BillingProvider):
    def __init__(self, config: dict):
        self.api_key = os.getenv("STRIPE_API_KEY", config.get("api_key", ""))

    def get_invoice(self, invoice_id: str) -> str:
        # TODO: stripe.Invoice.retrieve(invoice_id)
        raise NotImplementedError("Stripe get_invoice not yet implemented.")

    def process_refund(self, invoice_id: str, reason: str) -> str:
        # TODO: stripe.Refund.create(charge=invoice.charge, reason=reason)
        raise NotImplementedError("Stripe process_refund not yet implemented.")

    def cancel_subscription(self, subscription_id: str, reason: str) -> str:
        # TODO: stripe.Subscription.modify(subscription_id, cancel_at_period_end=True, metadata={"reason": reason})
        raise NotImplementedError("Stripe cancel_subscription not yet implemented.")

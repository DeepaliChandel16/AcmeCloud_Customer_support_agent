from datetime import datetime, timezone
from typing import Annotated

from agent_framework import tool
from pydantic import Field

_INVOICES = {
    "INV-1001": {"id": "INV-1001", "customer_id": "CUST-001", "amount": 49.99, "status": "paid", "date": "2026-03-01"},
    "INV-1002": {"id": "INV-1002", "customer_id": "CUST-001", "amount": 49.99, "status": "paid", "date": "2026-04-01"},
    "INV-1003": {"id": "INV-1003", "customer_id": "CUST-002", "amount": 199.99, "status": "paid", "date": "2026-04-01"},
    "INV-1004": {"id": "INV-1004", "customer_id": "CUST-003", "amount": 9.99, "status": "overdue", "date": "2026-03-01"},
}

_SUBSCRIPTIONS = {
    "SUB-001": {"id": "SUB-001", "customer_id": "CUST-001", "plan": "Pro", "status": "active", "renewal": "2026-05-01"},
    "SUB-002": {"id": "SUB-002", "customer_id": "CUST-002", "plan": "Enterprise", "status": "active", "renewal": "2026-05-01"},
    "SUB-003": {"id": "SUB-003", "customer_id": "CUST-003", "plan": "Starter", "status": "suspended", "renewal": "N/A"},
}


@tool(approval_mode="never_require")
def get_invoice(
    invoice_id: Annotated[str, Field(description="Invoice ID to look up")],
) -> str:
    """Retrieve invoice details."""
    inv = _INVOICES.get(invoice_id)
    if not inv:
        return f"Error: Invoice {invoice_id} not found."
    return (
        f"Invoice {inv['id']}: Customer={inv['customer_id']}, "
        f"Amount=${inv['amount']}, Status={inv['status']}, Date={inv['date']}."
    )


@tool(approval_mode="always_require")
def process_refund(
    invoice_id: Annotated[str, Field(description="Invoice ID to refund")],
    reason: Annotated[str, Field(description="Reason for the refund")],
) -> str:
    """Process a refund for an invoice. Requires human approval before execution."""
    inv = _INVOICES.get(invoice_id)
    if not inv:
        return f"Error: Invoice {invoice_id} not found."
    if inv["status"] == "refunded":
        return f"Invoice {invoice_id} has already been refunded."
    inv["status"] = "refunded"
    return (
        f"Refund of ${inv['amount']} processed for invoice {invoice_id}. "
        f"Reason: {reason}. Refund will appear in 5-10 business days."
    )


@tool(approval_mode="always_require")
def cancel_subscription(
    subscription_id: Annotated[str, Field(description="Subscription ID to cancel")],
    reason: Annotated[str, Field(description="Reason for cancellation")],
) -> str:
    """Cancel a customer subscription. Requires human approval before execution."""
    sub = _SUBSCRIPTIONS.get(subscription_id)
    if not sub:
        return f"Error: Subscription {subscription_id} not found."
    if sub["status"] == "cancelled":
        return f"Subscription {subscription_id} is already cancelled."
    sub["status"] = "cancelled"
    sub["cancelled_at"] = datetime.now(timezone.utc).isoformat()
    return (
        f"Subscription {subscription_id} (Plan: {sub['plan']}) cancelled. "
        f"Reason: {reason}. Access continues until current period ends."
    )

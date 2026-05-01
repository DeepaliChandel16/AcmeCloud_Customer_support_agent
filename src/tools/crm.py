from typing import Annotated

from agent_framework import tool
from pydantic import Field

_CUSTOMERS = {
    "CUST-001": {
        "id": "CUST-001",
        "name": "Alice Johnson",
        "email": "a***@example.com",
        "plan": "Pro",
        "status": "active",
        "verified": False,
        "security_answer": "fluffy",
    },
    "CUST-002": {
        "id": "CUST-002",
        "name": "Bob Smith",
        "email": "b***@example.com",
        "plan": "Enterprise",
        "status": "active",
        "verified": False,
        "security_answer": "rover",
    },
    "CUST-003": {
        "id": "CUST-003",
        "name": "Carol Davis",
        "email": "c***@example.com",
        "plan": "Starter",
        "status": "suspended",
        "verified": False,
        "security_answer": "sunshine",
    },
}


@tool(approval_mode="never_require")
def get_customer_profile(
    customer_id: Annotated[str, Field(description="Customer ID to look up")],
) -> str:
    """Retrieve a customer profile from the CRM. Sensitive fields are masked."""
    customer = _CUSTOMERS.get(customer_id)
    if not customer:
        return f"Error: Customer {customer_id} not found."
    return (
        f"Customer {customer['id']}: Name={customer['name']}, "
        f"Email={customer['email']}, Plan={customer['plan']}, "
        f"Status={customer['status']}."
    )


@tool(approval_mode="never_require")
def verify_identity(
    customer_id: Annotated[str, Field(description="Customer ID")],
    security_answer: Annotated[str, Field(description="Answer to the security question: What is your pet's name?")],
) -> str:
    """Verify a customer's identity using their security question answer. Must be called before account modifications."""
    customer = _CUSTOMERS.get(customer_id)
    if not customer:
        return f"Error: Customer {customer_id} not found."
    if security_answer.lower().strip() == customer["security_answer"]:
        customer["verified"] = True
        return f"Identity verified for customer {customer_id}."
    return f"Identity verification failed for customer {customer_id}. Incorrect security answer."


def is_verified(customer_id: str) -> bool:
    customer = _CUSTOMERS.get(customer_id)
    return customer["verified"] if customer else False

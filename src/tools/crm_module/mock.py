"""In-memory mock CRM provider for development and testing."""
from src.tools.interfaces import CRMProvider

_CUSTOMERS = {
    "CUST-001": {
        "id": "CUST-001", "name": "Alice Johnson", "email": "a***@example.com",
        "plan": "Pro", "status": "active", "verified": False, "security_answer": "fluffy",
    },
    "CUST-002": {
        "id": "CUST-002", "name": "Bob Smith", "email": "b***@example.com",
        "plan": "Enterprise", "status": "active", "verified": False, "security_answer": "rover",
    },
    "CUST-003": {
        "id": "CUST-003", "name": "Carol Davis", "email": "c***@example.com",
        "plan": "Starter", "status": "suspended", "verified": False, "security_answer": "sunshine",
    },
}


class MockCRM(CRMProvider):
    def get_customer_profile(self, customer_id: str) -> str:
        customer = _CUSTOMERS.get(customer_id)
        if not customer:
            return f"Error: Customer {customer_id} not found."
        return (
            f"Customer {customer['id']}: Name={customer['name']}, "
            f"Email={customer['email']}, Plan={customer['plan']}, Status={customer['status']}."
        )

    def verify_identity(self, customer_id: str, security_answer: str) -> str:
        customer = _CUSTOMERS.get(customer_id)
        if not customer:
            return f"Error: Customer {customer_id} not found."
        if security_answer.lower().strip() == customer["security_answer"]:
            customer["verified"] = True
            return f"Identity verified for customer {customer_id}."
        return f"Identity verification failed for customer {customer_id}. Incorrect security answer."

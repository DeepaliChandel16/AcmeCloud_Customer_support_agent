"""Abstract base interfaces for all tool domains.

Each domain (ticketing, CRM, billing, etc.) defines a base class here.
Concrete implementations (mock, Zendesk, Salesforce, etc.) inherit from these.
The factory in each domain's __init__.py selects the right implementation based on config.
"""
from abc import ABC, abstractmethod


class TicketingProvider(ABC):
    @abstractmethod
    def create_ticket(self, customer_id: str, subject: str, description: str, priority: str = "medium") -> str: ...

    @abstractmethod
    def update_ticket(self, ticket_id: str, status: str = "", note: str = "") -> str: ...

    @abstractmethod
    def get_ticket(self, ticket_id: str) -> str: ...


class CRMProvider(ABC):
    @abstractmethod
    def get_customer_profile(self, customer_id: str) -> str: ...

    @abstractmethod
    def verify_identity(self, customer_id: str, security_answer: str) -> str: ...


class BillingProvider(ABC):
    @abstractmethod
    def get_invoice(self, invoice_id: str) -> str: ...

    @abstractmethod
    def process_refund(self, invoice_id: str, reason: str) -> str: ...

    @abstractmethod
    def cancel_subscription(self, subscription_id: str, reason: str) -> str: ...


class AccountProvider(ABC):
    @abstractmethod
    def check_account_status(self, customer_id: str) -> str: ...

    @abstractmethod
    def reset_password(self, customer_id: str) -> str: ...


class TelemetryProvider(ABC):
    @abstractmethod
    def get_service_status(self, service_name: str = "") -> str: ...


class KnowledgeProvider(ABC):
    @abstractmethod
    def search_kb(self, query: str) -> str: ...

    @abstractmethod
    def get_policy(self, policy_name: str) -> str: ...


class ConversationStore(ABC):
    """Abstract store for cross-turn conversation memory."""

    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str, agent: str = "") -> None: ...

    @abstractmethod
    def get_history(self, session_id: str, limit: int = 50) -> list[dict]: ...

    @abstractmethod
    def list_sessions(self) -> list[dict]:
        """Return all sessions sorted by last activity. Each dict has: id, title, updated_at."""
        ...

    @abstractmethod
    def get_session_title(self, session_id: str) -> str: ...

    @abstractmethod
    def set_session_title(self, session_id: str, title: str) -> None: ...

    @abstractmethod
    def delete_session(self, session_id: str) -> None: ...

    @abstractmethod
    def clear_session(self, session_id: str) -> None: ...

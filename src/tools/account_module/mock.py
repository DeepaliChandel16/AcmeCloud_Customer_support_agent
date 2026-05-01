"""In-memory mock account provider for development and testing."""
from src.tools.interfaces import AccountProvider

_ACCOUNTS = {
    "CUST-001": {"status": "active", "mfa_enabled": True, "last_login": "2026-04-28T14:30:00Z"},
    "CUST-002": {"status": "active", "mfa_enabled": True, "last_login": "2026-04-29T09:15:00Z"},
    "CUST-003": {"status": "suspended", "mfa_enabled": False, "last_login": "2026-03-15T11:00:00Z"},
}


class MockAccount(AccountProvider):
    def check_account_status(self, customer_id: str) -> str:
        acct = _ACCOUNTS.get(customer_id)
        if not acct:
            return f"Error: Account for customer {customer_id} not found."
        return (
            f"Account {customer_id}: Status={acct['status']}, "
            f"MFA={'enabled' if acct['mfa_enabled'] else 'disabled'}, "
            f"Last login={acct['last_login']}."
        )

    def reset_password(self, customer_id: str) -> str:
        acct = _ACCOUNTS.get(customer_id)
        if not acct:
            return f"Error: Account for customer {customer_id} not found."
        return (
            f"Password reset link sent to the email on file for customer {customer_id}. "
            f"The link expires in 30 minutes."
        )

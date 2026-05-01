"""Central tool registry.

Creates @tool-decorated functions from provider instances based on config.
This is the single place where config-driven provider selection happens.
Agents consume the tools returned here -- they never import providers directly.
"""
import logging
import time
from typing import Annotated

from agent_framework import tool
from pydantic import Field

from src.config import AppConfig
from src.tools.ticketing import get_ticketing_provider
from src.tools.knowledge_base import get_knowledge_provider
from src.tools.crm_module import get_crm_provider
from src.tools.billing_module import get_billing_provider
from src.tools.account_module import get_account_provider
from src.tools.telemetry_module import get_telemetry_provider

logger = logging.getLogger("acmecloud.tools")


def _safe_call(func, *args, **kwargs):
    """Wrap provider calls with error handling for graceful degradation."""
    name = getattr(func, "__name__", str(func))
    logger.info("TOOL CALL: %s(%s)", name, ", ".join([repr(a) for a in args]))
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("TOOL OK: %s (%.0fms) -> %s", name, elapsed, str(result)[:200])
        return result
    except NotImplementedError:
        logger.warning("TOOL NOT IMPLEMENTED: %s", name)
        return "Error: This integration is not yet configured. Please contact your administrator."
    except Exception as e:
        logger.error("TOOL ERROR: %s -> %s: %s", name, type(e).__name__, e)
        return f"Error: Tool temporarily unavailable ({type(e).__name__}). Please try again or ask for human assistance."


class ToolRegistry:
    """Builds all @tool functions from config-driven providers."""

    def __init__(self, config: AppConfig):
        integrations = config.integrations
        self._ticketing = get_ticketing_provider(integrations.get("ticketing", {}))
        self._knowledge = get_knowledge_provider(integrations.get("knowledge", {}))
        self._crm = get_crm_provider(integrations.get("crm", {}))
        self._billing = get_billing_provider(integrations.get("billing", {}))
        self._account = get_account_provider(integrations.get("account", {}))
        self._telemetry = get_telemetry_provider(integrations.get("telemetry", {}))
        self._build_tools()

    def _build_tools(self):
        ticketing = self._ticketing
        knowledge = self._knowledge
        crm = self._crm
        billing = self._billing
        account = self._account
        telemetry = self._telemetry

        # --- Ticketing tools ---
        @tool(approval_mode="never_require")
        def create_ticket(
            customer_id: Annotated[str, Field(description="Customer ID")],
            subject: Annotated[str, Field(description="Short summary of the issue")],
            description: Annotated[str, Field(description="Detailed description of the issue")],
            priority: Annotated[str, Field(description="Priority: low, medium, high, urgent")] = "medium",
        ) -> str:
            """Create a new support ticket in the ticketing system."""
            return _safe_call(ticketing.create_ticket, customer_id, subject, description, priority)

        @tool(approval_mode="never_require")
        def update_ticket(
            ticket_id: Annotated[str, Field(description="Ticket ID to update")],
            status: Annotated[str, Field(description="New status: open, in_progress, resolved, closed")] = "",
            note: Annotated[str, Field(description="Note to add to the ticket")] = "",
        ) -> str:
            """Update an existing support ticket with a new status or note."""
            return _safe_call(ticketing.update_ticket, ticket_id, status, note)

        @tool(approval_mode="never_require")
        def get_ticket(
            ticket_id: Annotated[str, Field(description="Ticket ID to look up")],
        ) -> str:
            """Retrieve details of a support ticket."""
            return _safe_call(ticketing.get_ticket, ticket_id)

        # --- Knowledge tools ---
        @tool(approval_mode="never_require")
        def search_kb(
            query: Annotated[str, Field(description="Search query to find relevant knowledge base articles")],
        ) -> str:
            """Search the knowledge base for articles matching the query."""
            return _safe_call(knowledge.search_kb, query)

        @tool(approval_mode="never_require")
        def get_policy(
            policy_name: Annotated[str, Field(description="Policy name: data-retention, sla, or acceptable-use")],
        ) -> str:
            """Retrieve a specific AcmeCloud policy document."""
            return _safe_call(knowledge.get_policy, policy_name)

        # --- CRM tools ---
        @tool(approval_mode="never_require")
        def get_customer_profile(
            customer_id: Annotated[str, Field(description="Customer ID to look up")],
        ) -> str:
            """Retrieve a customer profile from the CRM. Sensitive fields are masked."""
            return _safe_call(crm.get_customer_profile, customer_id)

        @tool(approval_mode="never_require")
        def verify_identity(
            customer_id: Annotated[str, Field(description="Customer ID")],
            security_answer: Annotated[str, Field(description="Answer to the security question: What is your pet's name?")],
        ) -> str:
            """Verify a customer's identity. Must be called before account modifications."""
            return _safe_call(crm.verify_identity, customer_id, security_answer)

        # --- Billing tools ---
        @tool(approval_mode="never_require")
        def get_invoice(
            invoice_id: Annotated[str, Field(description="Invoice ID to look up")],
        ) -> str:
            """Retrieve invoice details."""
            return _safe_call(billing.get_invoice, invoice_id)

        @tool(approval_mode="always_require")
        def process_refund(
            invoice_id: Annotated[str, Field(description="Invoice ID to refund")],
            reason: Annotated[str, Field(description="Reason for the refund")],
        ) -> str:
            """Process a refund for an invoice. Requires human approval."""
            return _safe_call(billing.process_refund, invoice_id, reason)

        @tool(approval_mode="always_require")
        def cancel_subscription(
            subscription_id: Annotated[str, Field(description="Subscription ID to cancel")],
            reason: Annotated[str, Field(description="Reason for cancellation")],
        ) -> str:
            """Cancel a customer subscription. Requires human approval."""
            return _safe_call(billing.cancel_subscription, subscription_id, reason)

        # --- Account tools ---
        @tool(approval_mode="never_require")
        def check_account_status(
            customer_id: Annotated[str, Field(description="Customer ID to check")],
        ) -> str:
            """Check the current status of a customer account."""
            return _safe_call(account.check_account_status, customer_id)

        @tool(approval_mode="always_require")
        def reset_password(
            customer_id: Annotated[str, Field(description="Customer ID whose password to reset")],
        ) -> str:
            """Reset a customer's account password. Requires human approval."""
            return _safe_call(account.reset_password, customer_id)

        # --- Telemetry tools ---
        @tool(approval_mode="never_require")
        def get_service_status(
            service_name: Annotated[str, Field(description="Service name, e.g. api-gateway, auth-service")] = "",
        ) -> str:
            """Get the current operational status of AcmeCloud services. Read-only."""
            return _safe_call(telemetry.get_service_status, service_name)

        # Store references
        self.create_ticket = create_ticket
        self.update_ticket = update_ticket
        self.get_ticket = get_ticket
        self.search_kb = search_kb
        self.get_policy = get_policy
        self.get_customer_profile = get_customer_profile
        self.verify_identity = verify_identity
        self.get_invoice = get_invoice
        self.process_refund = process_refund
        self.cancel_subscription = cancel_subscription
        self.check_account_status = check_account_status
        self.reset_password = reset_password
        self.get_service_status = get_service_status

    def knowledge_tools(self) -> list:
        return [self.search_kb, self.get_policy, self.get_service_status]

    def account_tools(self) -> list:
        return [self.check_account_status, self.reset_password, self.get_customer_profile, self.verify_identity]

    def billing_tools(self) -> list:
        return [self.get_invoice, self.process_refund, self.cancel_subscription, self.get_customer_profile]

    def ticket_tools(self) -> list:
        return [self.create_ticket, self.update_ticket, self.get_ticket]

import uuid
from datetime import datetime, timezone
from typing import Annotated

from agent_framework import tool
from pydantic import Field

_TICKETS: dict[str, dict] = {}


@tool(approval_mode="never_require")
def create_ticket(
    customer_id: Annotated[str, Field(description="Customer ID")],
    subject: Annotated[str, Field(description="Short summary of the issue")],
    description: Annotated[str, Field(description="Detailed description of the issue")],
    priority: Annotated[str, Field(description="Priority: low, medium, high, urgent")] = "medium",
) -> str:
    """Create a new support ticket in the ticketing system."""
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    _TICKETS[ticket_id] = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return f"Ticket {ticket_id} created successfully. Subject: {subject}, Priority: {priority}, Status: open."


@tool(approval_mode="never_require")
def update_ticket(
    ticket_id: Annotated[str, Field(description="Ticket ID to update")],
    status: Annotated[str, Field(description="New status: open, in_progress, resolved, closed")] = "",
    note: Annotated[str, Field(description="Note to add to the ticket")] = "",
) -> str:
    """Update an existing support ticket with a new status or note."""
    if ticket_id not in _TICKETS:
        return f"Error: Ticket {ticket_id} not found."
    ticket = _TICKETS[ticket_id]
    updates = []
    if status:
        ticket["status"] = status
        updates.append(f"status -> {status}")
    if note:
        ticket.setdefault("notes", []).append(
            {"note": note, "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        updates.append("note added")
    ticket["updated_at"] = datetime.now(timezone.utc).isoformat()
    return f"Ticket {ticket_id} updated: {', '.join(updates)}."


@tool(approval_mode="never_require")
def get_ticket(
    ticket_id: Annotated[str, Field(description="Ticket ID to look up")],
) -> str:
    """Retrieve details of a support ticket."""
    if ticket_id not in _TICKETS:
        return f"Error: Ticket {ticket_id} not found."
    t = _TICKETS[ticket_id]
    return (
        f"Ticket {t['ticket_id']}: Subject='{t['subject']}', Status={t['status']}, "
        f"Priority={t['priority']}, Customer={t['customer_id']}, "
        f"Created={t['created_at']}, Updated={t['updated_at']}."
    )

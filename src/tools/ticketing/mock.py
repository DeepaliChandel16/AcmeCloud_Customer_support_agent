"""In-memory mock ticketing provider for development and testing."""
import uuid
from datetime import datetime, timezone

from src.tools.interfaces import TicketingProvider

_TICKETS: dict[str, dict] = {}


class MockTicketing(TicketingProvider):
    def create_ticket(self, customer_id: str, subject: str, description: str, priority: str = "medium") -> str:
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

    def update_ticket(self, ticket_id: str, status: str = "", note: str = "") -> str:
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

    def get_ticket(self, ticket_id: str) -> str:
        if ticket_id not in _TICKETS:
            return f"Error: Ticket {ticket_id} not found."
        t = _TICKETS[ticket_id]
        return (
            f"Ticket {t['ticket_id']}: Subject='{t['subject']}', Status={t['status']}, "
            f"Priority={t['priority']}, Customer={t['customer_id']}, "
            f"Created={t['created_at']}, Updated={t['updated_at']}."
        )

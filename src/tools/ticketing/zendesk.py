"""Zendesk ticketing provider stub.

To activate: set integrations.ticketing.provider = "zendesk" in settings.yaml
and provide ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN env vars.

Implementation notes:
- Uses Zendesk REST API v2: https://developer.zendesk.com/api-reference/
- Auth: email/token basic auth or OAuth
- Map internal priority (low/medium/high/urgent) to Zendesk priority values
- Map internal status (open/in_progress/resolved/closed) to Zendesk status
"""
import os

from src.tools.interfaces import TicketingProvider


class ZendeskTicketing(TicketingProvider):
    def __init__(self, config: dict):
        self.subdomain = os.getenv("ZENDESK_SUBDOMAIN", config.get("subdomain", ""))
        self.email = os.getenv("ZENDESK_EMAIL", config.get("email", ""))
        self.api_token = os.getenv("ZENDESK_API_TOKEN", config.get("api_token", ""))
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"

    def create_ticket(self, customer_id: str, subject: str, description: str, priority: str = "medium") -> str:
        # TODO: Implement Zendesk API call
        # POST /api/v2/tickets.json
        # Body: {"ticket": {"subject": subject, "description": description, "priority": priority,
        #        "requester": {"name": customer_id}, "tags": ["acmecloud-agent"]}}
        raise NotImplementedError("Zendesk create_ticket not yet implemented. Add httpx POST to /api/v2/tickets.json")

    def update_ticket(self, ticket_id: str, status: str = "", note: str = "") -> str:
        # TODO: Implement Zendesk API call
        # PUT /api/v2/tickets/{ticket_id}.json
        # Body: {"ticket": {"status": status, "comment": {"body": note, "public": false}}}
        raise NotImplementedError("Zendesk update_ticket not yet implemented. Add httpx PUT to /api/v2/tickets/{id}.json")

    def get_ticket(self, ticket_id: str) -> str:
        # TODO: Implement Zendesk API call
        # GET /api/v2/tickets/{ticket_id}.json
        raise NotImplementedError("Zendesk get_ticket not yet implemented. Add httpx GET to /api/v2/tickets/{id}.json")

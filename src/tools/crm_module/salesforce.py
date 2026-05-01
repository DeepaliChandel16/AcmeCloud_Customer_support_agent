"""Salesforce CRM provider stub.

To activate: set integrations.crm.provider = "salesforce" in settings.yaml
and provide SF_INSTANCE_URL, SF_CLIENT_ID, SF_CLIENT_SECRET, SF_USERNAME, SF_PASSWORD env vars.

Implementation notes:
- Auth: OAuth 2.0 username-password flow or JWT bearer flow
- Query: SOQL via /services/data/vXX.0/query?q=SELECT+...+FROM+Contact
- Identity verification: match against custom field (SecurityQuestion__c)
- Mask sensitive fields before returning
"""
import os

from src.tools.interfaces import CRMProvider


class SalesforceCRM(CRMProvider):
    def __init__(self, config: dict):
        self.instance_url = os.getenv("SF_INSTANCE_URL", config.get("instance_url", ""))
        self.client_id = os.getenv("SF_CLIENT_ID", config.get("client_id", ""))
        self.client_secret = os.getenv("SF_CLIENT_SECRET", config.get("client_secret", ""))

    def get_customer_profile(self, customer_id: str) -> str:
        # TODO: SOQL query
        # GET /services/data/v59.0/query?q=SELECT+Name,Email,Plan__c,Status__c+FROM+Contact+WHERE+Id='{customer_id}'
        raise NotImplementedError("Salesforce get_customer_profile not yet implemented.")

    def verify_identity(self, customer_id: str, security_answer: str) -> str:
        # TODO: Query SecurityQuestion__c custom field and compare
        raise NotImplementedError("Salesforce verify_identity not yet implemented.")

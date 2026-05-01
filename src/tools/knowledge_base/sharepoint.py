"""SharePoint knowledge base provider stub.

To activate: set integrations.knowledge.provider = "sharepoint" in settings.yaml
and provide AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SHAREPOINT_SITE_URL env vars.

Implementation notes:
- Uses Microsoft Graph API: https://learn.microsoft.com/en-us/graph/api/resources/search-api-overview
- Auth: MSAL client credentials flow -> access token
- Search: POST /search/query with KQL queries across SharePoint site pages/documents
- For vector search: index SharePoint content into Azure AI Search with embeddings
- Policies can be stored as tagged pages in a SharePoint list
"""
import os

from src.tools.interfaces import KnowledgeProvider


class SharePointKnowledge(KnowledgeProvider):
    def __init__(self, config: dict):
        self.tenant_id = os.getenv("AZURE_TENANT_ID", config.get("tenant_id", ""))
        self.client_id = os.getenv("AZURE_CLIENT_ID", config.get("client_id", ""))
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", config.get("client_secret", ""))
        self.site_url = os.getenv("SHAREPOINT_SITE_URL", config.get("site_url", ""))

    def search_kb(self, query: str) -> str:
        # TODO: Implement Graph API search
        # 1. Acquire token via MSAL: POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
        # 2. POST https://graph.microsoft.com/v1.0/search/query
        #    Body: {"requests": [{"entityTypes": ["driveItem", "listItem"],
        #           "query": {"queryString": query}, "from": 0, "size": 5}]}
        # 3. Parse hits, return formatted results
        raise NotImplementedError("SharePoint search_kb not yet implemented. Add Graph API search call.")

    def get_policy(self, policy_name: str) -> str:
        # TODO: Implement Graph API list item fetch
        # GET /sites/{site-id}/lists/{policies-list-id}/items?$filter=fields/PolicyName eq '{policy_name}'
        raise NotImplementedError("SharePoint get_policy not yet implemented. Add Graph API list query.")

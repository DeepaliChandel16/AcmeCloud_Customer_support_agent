"""Azure Entra ID (formerly Azure AD) account provider stub.

To activate: set integrations.account.provider = "entra" in settings.yaml
and provide AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET env vars.

Implementation notes:
- Auth: MSAL client credentials or on-behalf-of flow
- Check status: GET /users/{id}?$select=accountEnabled,signInActivity
- Reset password: POST /users/{id}/authentication/passwordMethods/{id}/resetPassword
- MFA status: GET /users/{id}/authentication/methods
- Requires Directory.ReadWrite.All or UserAuthenticationMethod.ReadWrite.All permissions
"""
import os

from src.tools.interfaces import AccountProvider


class EntraAccount(AccountProvider):
    def __init__(self, config: dict):
        self.tenant_id = os.getenv("AZURE_TENANT_ID", config.get("tenant_id", ""))
        self.client_id = os.getenv("AZURE_CLIENT_ID", config.get("client_id", ""))
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", config.get("client_secret", ""))

    def check_account_status(self, customer_id: str) -> str:
        # TODO: Graph API call
        # GET https://graph.microsoft.com/v1.0/users/{customer_id}?$select=accountEnabled,signInActivity
        raise NotImplementedError("Entra check_account_status not yet implemented.")

    def reset_password(self, customer_id: str) -> str:
        # TODO: Graph API call
        # POST https://graph.microsoft.com/v1.0/users/{customer_id}/authentication/passwordMethods/{id}/resetPassword
        raise NotImplementedError("Entra reset_password not yet implemented.")

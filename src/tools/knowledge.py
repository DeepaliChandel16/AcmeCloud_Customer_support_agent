from typing import Annotated

from agent_framework import tool
from pydantic import Field

_KB_ARTICLES = {
    "KB-001": {
        "title": "How to reset your password",
        "content": (
            "To reset your password: 1) Go to acmecloud.com/reset. 2) Enter your email. "
            "3) Click the reset link sent to your email. 4) Choose a new password (min 12 chars, "
            "must include uppercase, lowercase, number, and special character)."
        ),
        "tags": ["password", "reset", "account", "login"],
    },
    "KB-002": {
        "title": "Refund policy",
        "content": (
            "AcmeCloud offers full refunds within 30 days of purchase for annual plans. "
            "Monthly plans can be cancelled anytime but are not refundable for the current period. "
            "Refunds are processed within 5-10 business days to the original payment method."
        ),
        "tags": ["refund", "billing", "policy", "cancel"],
    },
    "KB-003": {
        "title": "Supported file formats for upload",
        "content": (
            "AcmeCloud supports the following file formats: PDF, DOCX, XLSX, PNG, JPG, GIF, "
            "MP4, CSV, JSON, and XML. Maximum file size is 500MB per file, 5GB per upload batch."
        ),
        "tags": ["upload", "files", "formats", "storage"],
    },
    "KB-004": {
        "title": "Two-Factor Authentication (2FA) setup",
        "content": (
            "To enable 2FA: 1) Go to Settings > Security. 2) Click 'Enable 2FA'. "
            "3) Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.). "
            "4) Enter the 6-digit code to verify. Backup codes are provided for account recovery."
        ),
        "tags": ["2fa", "mfa", "security", "authentication"],
    },
    "KB-005": {
        "title": "Subscription plans and pricing",
        "content": (
            "AcmeCloud Plans: Starter ($9.99/mo) - 10GB storage, 1 user. "
            "Pro ($49.99/mo) - 100GB storage, 5 users, priority support. "
            "Enterprise ($199.99/mo) - 1TB storage, unlimited users, dedicated support, SLA."
        ),
        "tags": ["plans", "pricing", "subscription", "billing"],
    },
    "KB-006": {
        "title": "API rate limits",
        "content": (
            "API rate limits per plan: Starter - 100 req/min. Pro - 1000 req/min. "
            "Enterprise - 10,000 req/min. Exceeding limits returns HTTP 429. "
            "Use the X-RateLimit-Remaining header to monitor usage."
        ),
        "tags": ["api", "rate limit", "developer", "integration"],
    },
}

_POLICIES = {
    "data-retention": (
        "AcmeCloud retains customer data for 90 days after account closure. "
        "Data can be exported anytime before deletion. Enterprise customers "
        "can request extended retention up to 1 year."
    ),
    "sla": (
        "AcmeCloud SLA: Enterprise plan guarantees 99.95% uptime. "
        "Credits are issued for downtime exceeding SLA: 10% credit for 99.0-99.95%, "
        "25% credit for 95.0-99.0%, 50% credit for below 95.0%."
    ),
    "acceptable-use": (
        "Users must not use AcmeCloud for illegal activities, spam, malware distribution, "
        "cryptocurrency mining, or storing prohibited content. Violations result in "
        "immediate account suspension."
    ),
}


@tool(approval_mode="never_require")
def search_kb(
    query: Annotated[str, Field(description="Search query to find relevant knowledge base articles")],
) -> str:
    """Search the knowledge base for articles matching the query."""
    query_lower = query.lower()
    results = []
    for article_id, article in _KB_ARTICLES.items():
        score = 0
        for tag in article["tags"]:
            if tag in query_lower:
                score += 2
        if any(word in article["title"].lower() for word in query_lower.split()):
            score += 1
        if any(word in article["content"].lower() for word in query_lower.split()):
            score += 1
        if score > 0:
            results.append((score, article_id, article))
    if not results:
        return "No matching articles found in the knowledge base."
    results.sort(key=lambda x: x[0], reverse=True)
    lines = []
    for _, aid, art in results[:3]:
        lines.append(f"[{aid}] {art['title']}: {art['content']}")
    return "\n\n".join(lines)


@tool(approval_mode="never_require")
def get_policy(
    policy_name: Annotated[str, Field(description="Policy name: data-retention, sla, or acceptable-use")],
) -> str:
    """Retrieve a specific AcmeCloud policy document."""
    policy = _POLICIES.get(policy_name)
    if not policy:
        available = ", ".join(_POLICIES.keys())
        return f"Error: Policy '{policy_name}' not found. Available: {available}."
    return f"Policy '{policy_name}': {policy}"

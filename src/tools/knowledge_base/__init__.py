"""Knowledge base tool factory."""
from src.tools.interfaces import KnowledgeProvider


def get_knowledge_provider(config: dict) -> KnowledgeProvider:
    provider = config.get("provider", "mock")
    if provider == "sharepoint":
        from src.tools.knowledge_base.sharepoint import SharePointKnowledge
        return SharePointKnowledge(config)
    elif provider == "mock":
        from src.tools.knowledge_base.mock import MockKnowledge
        return MockKnowledge()
    else:
        raise ValueError(f"Unknown knowledge provider: {provider}")

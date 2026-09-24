from typing import Any

from app.infrastructure.providers.local_provider import LocalProposalProvider


class AzureAISearchProvider(LocalProposalProvider):
    """Azure AI Search adapter boundary for grounded retrieval."""

    def __init__(self, endpoint: str | None = None, **kwargs: Any):
        super().__init__(provider_name="azure-ai-search", **kwargs)
        self.endpoint = endpoint

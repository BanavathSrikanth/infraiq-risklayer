from typing import Any

from app.infrastructure.providers.local_provider import LocalProposalProvider


class DocumentIntelligenceProvider(LocalProposalProvider):
    """Document Intelligence adapter boundary.

    Azure Document Intelligence SDK calls belong only in this adapter. The
    adapter maps OCR/layout output into the shared proposal contract.
    """

    def __init__(self, endpoint: str | None = None, **kwargs: Any):
        super().__init__(provider_name="azure-document-intelligence", **kwargs)
        self.endpoint = endpoint

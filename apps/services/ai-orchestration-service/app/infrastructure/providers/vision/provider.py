from typing import Any

from app.infrastructure.providers.local_provider import LocalProposalProvider


class VisionProvider(LocalProposalProvider):
    """Vision adapter boundary for image-based proposal generation."""

    def __init__(self, endpoint: str | None = None, **kwargs: Any):
        super().__init__(provider_name="azure-vision", **kwargs)
        self.endpoint = endpoint

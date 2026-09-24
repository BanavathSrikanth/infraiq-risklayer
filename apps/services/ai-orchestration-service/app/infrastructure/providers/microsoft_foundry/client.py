from typing import Any

from app.domain.schemas import AnalysisRequest
from app.infrastructure.providers.local_provider import LocalProposalProvider


class MicrosoftFoundryProvider(LocalProposalProvider):
    """Provider seam for Microsoft Foundry integration.

    The production adapter should call Foundry here and map its response into
    the shared proposal contract. Persistence remains outside this provider.
    """

    def __init__(self, endpoint: str | None = None, **kwargs: Any):
        super().__init__(provider_name="microsoft-foundry", **kwargs)
        self.endpoint = endpoint

    def analyze(self, operation: str, request: AnalysisRequest):
        if not self.endpoint:
            return super().analyze(operation, request)
        raise NotImplementedError("Configure the Foundry SDK adapter before enabling this provider")

from app.config import Settings
from app.infrastructure.providers.azure_ai_search import AzureAISearchProvider
from app.infrastructure.providers.document_intelligence import DocumentIntelligenceProvider
from app.infrastructure.providers.local_provider import LocalProposalProvider
from app.infrastructure.providers.microsoft_foundry import MicrosoftFoundryProvider
from app.infrastructure.providers.vision import VisionProvider
from app.infrastructure.providers.provider import AIProvider


class ProviderRegistry:
    """Builds provider adapters; application code depends only on AIProvider."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def create(self) -> AIProvider:
        common = {
            "model_name": self.settings.model_name,
            "model_version": self.settings.model_version,
        }
        providers: dict[str, AIProvider] = {
            "local-deterministic": LocalProposalProvider(
                provider_name="local-deterministic", **common
            ),
            "microsoft-foundry": MicrosoftFoundryProvider(
                endpoint=self.settings.foundry_endpoint, **common
            ),
            "document-intelligence": DocumentIntelligenceProvider(
                endpoint=self.settings.document_intelligence_endpoint, **common
            ),
            "azure-ai-search": AzureAISearchProvider(
                endpoint=self.settings.ai_search_endpoint, **common
            ),
            "vision": VisionProvider(
                endpoint=self.settings.vision_endpoint, **common
            ),
        }
        try:
            return providers[self.settings.model_provider]
        except KeyError as exc:
            supported = ", ".join(sorted(providers))
            raise ValueError(
                f"Unsupported AI provider '{self.settings.model_provider}'. Supported: {supported}"
            ) from exc

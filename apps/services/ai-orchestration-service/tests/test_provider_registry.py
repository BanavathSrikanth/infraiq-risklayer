import pytest

from app.config import Settings
from app.infrastructure.providers.azure_ai_search import AzureAISearchProvider
from app.infrastructure.providers.document_intelligence import DocumentIntelligenceProvider
from app.infrastructure.providers.microsoft_foundry import MicrosoftFoundryProvider
from app.infrastructure.providers.registry import ProviderRegistry
from app.infrastructure.providers.vision import VisionProvider


@pytest.mark.parametrize(
    ("provider_name", "provider_type"),
    [
        ("microsoft-foundry", MicrosoftFoundryProvider),
        ("document-intelligence", DocumentIntelligenceProvider),
        ("azure-ai-search", AzureAISearchProvider),
        ("vision", VisionProvider),
    ],
)
def test_registry_selects_provider_adapter(provider_name, provider_type):
    provider = ProviderRegistry(Settings(model_provider=provider_name)).create()
    assert isinstance(provider, provider_type)


def test_registry_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        ProviderRegistry(Settings(model_provider="unknown")).create()

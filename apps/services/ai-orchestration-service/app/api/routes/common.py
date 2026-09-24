from fastapi import Depends

from app.application.orchestration import AIOrchestrationService
from app.config import get_settings
from app.infrastructure.providers.registry import ProviderRegistry


def get_orchestration_service() -> AIOrchestrationService:
    settings = get_settings()
    provider = ProviderRegistry(settings).create()
    return AIOrchestrationService(provider)


OrchestrationDependency = Depends(get_orchestration_service)

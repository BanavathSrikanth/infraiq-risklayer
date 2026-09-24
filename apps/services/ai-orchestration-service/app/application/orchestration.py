from ai.schemas import AIProposalResponse
from app.domain.schemas import AnalysisRequest
from app.infrastructure.providers.provider import AIProvider


class AIOrchestrationService:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def propose(self, operation: str, request: AnalysisRequest) -> AIProposalResponse:
        return self.provider.analyze(operation, request)

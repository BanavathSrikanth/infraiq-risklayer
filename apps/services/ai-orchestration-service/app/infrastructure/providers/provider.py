from typing import Protocol

from ai.schemas import AIProposalResponse
from app.domain.schemas import AnalysisRequest


class AIProvider(Protocol):
    def analyze(self, operation: str, request: AnalysisRequest) -> AIProposalResponse:
        ...

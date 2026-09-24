from fastapi import APIRouter, Depends

from ai.schemas import AIProposalResponse
from app.application.orchestration import AIOrchestrationService
from app.domain.schemas import AnalysisRequest
from app.api.routes.common import get_orchestration_service

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/propose", response_model=AIProposalResponse)
def propose_evaluation(
    request: AnalysisRequest,
    service: AIOrchestrationService = Depends(get_orchestration_service),
) -> AIProposalResponse:
    return service.propose("evaluation", request)

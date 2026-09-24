from fastapi import APIRouter, Depends

from ai.schemas import AIProposalResponse
from app.application.orchestration import AIOrchestrationService
from app.domain.schemas import AnalysisRequest
from app.api.routes.common import get_orchestration_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/propose", response_model=AIProposalResponse)
def propose_retrieval(
    request: AnalysisRequest,
    service: AIOrchestrationService = Depends(get_orchestration_service),
) -> AIProposalResponse:
    return service.propose("rag", request)

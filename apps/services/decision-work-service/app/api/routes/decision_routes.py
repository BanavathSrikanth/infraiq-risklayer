from fastapi import APIRouter, Depends, HTTPException

from app.application.services.decision_service import DecisionApplicationService
from app.infrastructure.repositories.decision_repository import DecisionRepository

router = APIRouter(prefix="/decisions", tags=["decisions"])


def get_decision_service() -> DecisionApplicationService:
    return DecisionApplicationService(DecisionRepository())


@router.post("")
async def create_decision(
    payload: dict,
    service: DecisionApplicationService = Depends(get_decision_service),
):
    try:
        decision = service.create_decision(
            decision_id=payload["decision_id"],
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
            recommendation_id=payload["recommendation_id"],
            decided_by=payload.get("decided_by", ""),
            outcome=payload.get("outcome", "approved"),
            rationale=payload.get("rationale", ""),
            conditions=payload.get("conditions"),
        )
        return {
            "decision_id": decision.decision_id,
            "asset_id": decision.asset_id,
            "tenant_id": decision.tenant_id,
            "recommendation_id": decision.recommendation_id,
            "outcome": decision.outcome,
            "decided_by": decision.decided_by,
            "rationale": decision.rationale,
            "conditions": decision.conditions or [],
            "approved": decision.approved,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{decision_id}/approve")
async def approve_decision(
    decision_id: str,
    service: DecisionApplicationService = Depends(get_decision_service),
):
    try:
        decision = service.approve_decision(decision_id)
        return {
            "decision_id": decision.decision_id,
            "approved": decision.approved,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

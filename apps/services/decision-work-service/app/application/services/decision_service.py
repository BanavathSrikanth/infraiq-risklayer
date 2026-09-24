from app.domain.entities.decision import Decision
from app.infrastructure.repositories.decision_repository import DecisionRepository


class DecisionApplicationService:
    def __init__(self, repository: DecisionRepository):
        self.repository = repository

    def create_decision(
        self,
        decision_id: str,
        asset_id: str,
        tenant_id: str,
        recommendation_id: str,
        decided_by: str = "",
        outcome: str = "approved",
        rationale: str = "",
        conditions: list[str] | None = None,
    ) -> Decision:
        decision = Decision(
            decision_id=decision_id,
            asset_id=asset_id,
            tenant_id=tenant_id,
            recommendation_id=recommendation_id,
            decided_by=decided_by,
            outcome=outcome,
            rationale=rationale,
            conditions=conditions,
        )
        return self.repository.save(decision)

    def approve_decision(self, decision_id: str) -> Decision:
        decision = self.repository.get_by_id(decision_id)
        if decision is None:
            raise ValueError(f"Decision {decision_id} not found")
        decision.outcome = "approved"
        return self.repository.update(decision)

    def list_for_asset(self, tenant_id: str, asset_id: str) -> list[Decision]:
        return self.repository.list_by_asset(tenant_id, asset_id)

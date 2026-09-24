from typing import Dict, List, Optional

from app.domain.entities.decision import Decision


class DecisionRepository:
    def __init__(self):
        self._store: Dict[str, Decision] = {}

    def save(self, decision: Decision) -> Decision:
        self._store[decision.decision_id] = decision
        return decision

    def get_by_id(self, decision_id: str) -> Optional[Decision]:
        return self._store.get(decision_id)

    def update(self, decision: Decision) -> Decision:
        self._store[decision.decision_id] = decision
        return decision

    def list_by_asset(self, tenant_id: str, asset_id: str) -> List[Decision]:
        return [
            item
            for item in self._store.values()
            if item.tenant_id == tenant_id and item.asset_id == asset_id
        ]

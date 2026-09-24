from typing import Any

from app.domain.schemas.risk_input import VesInput
from app.application.scoring.rule_loader import load_rules


class VesCalculator:
    """Calculate the Vegetation Exposure Score (VES)."""

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

    def calculate(self, data: VesInput) -> float:
        weights = self.rules["weights"]
        normalized_score = (
            data.proximity_factor * weights["proximity"]
            + data.density_factor * weights["density"]
            + data.clearance_factor * weights["clearance"]
            + data.overlap_factor * weights["overlap"]
            + data.encroach_factor * weights["encroach"]
        )
        return round(self._clamp(normalized_score * 100), 2)

from typing import Any, Dict

from app.domain.schemas.risk_input import CqsInput
from app.application.scoring.rule_loader import load_rules


class CqsCalculator:
    """Calculate the Consequence Score (CQS)."""

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _normalize(value: float, maximum: float) -> float:
        if maximum <= 0:
            return 0.0

        return min(1.0, value / maximum)

    def calculate(self, data: CqsInput) -> float:
        normalization = self.rules["normalization"]
        weights = self.rules["weights"]

        population_factor = self._normalize(
            data.population_density_1km,
            normalization["population_density_1km_max"],
        )
        critical_factor = self._normalize(
            data.critical_facilities_2km,
            normalization["critical_facilities_2km_max"],
        )
        customer_factor = self._normalize(
            data.customers_on_circuit_segment,
            normalization["customers_on_circuit_segment_max"],
        )
        normalized_road_density = self._normalize(
            data.road_density,
            normalization["road_density_max"],
        )
        egress_factor = 1.0 - normalized_road_density

        normalized_score = (
            population_factor * weights["population"]
            + critical_factor * weights["critical"]
            + customer_factor * weights["customer"]
            + egress_factor * weights["egress"]
        )
        return round(min(100.0, max(0.0, normalized_score * 100)), 2)
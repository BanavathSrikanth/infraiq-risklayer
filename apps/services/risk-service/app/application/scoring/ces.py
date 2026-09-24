from typing import Any, Dict

from app.domain.schemas.risk_input import CesInput
from app.application.scoring.rule_loader import load_rules


class CesCalculator:
    """Calculate the Chronic Exposure Score (CES)."""

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    def calculate(self, data: CesInput) -> float:
        weights = self.rules["weights"]
        hftd_factor = self.rules["hftd_factors"][data.hftd_tier]
        fhsz_factor = self.rules["fhsz_factors"][data.fhsz_level]
        fuel_factor = data.landfire_ros_class / self.rules["fuel"]["maximum_class"]
        slope_factor = min(
            1.0,
            data.slope_deg / self.rules["slope"]["normalization_degrees"],
        )
        wind_factor = min(
            1.0,
            data.p95_historical_gust_mps
            / self.rules["historical_wind"]["normalization_mps"],
        )
        normalized_score = (
            hftd_factor * weights["hftd"]
            + fhsz_factor * weights["fhsz"]
            + fuel_factor * weights["fuel"]
            + slope_factor * weights["slope"]
            + wind_factor * weights["wind"]
        )
        return round(min(100.0, max(0.0, normalized_score * 100)), 2)
from typing import Any

from app.application.scoring.rule_loader import load_rules


class OpsCalculator:
    """Calculate the Operational Priority Score (OPS)."""

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _clamp(score: float) -> float:
        return max(0.0, min(100.0, score))

    def calculate(
        self,
        *,
        ahs: float,
        ces: float,
        cqs: float,
        days_overdue: float = 0.0,
        work_already_scheduled: bool = False,
    ) -> float:
        weights = self.rules["weights"]
        base = (
            ahs * weights["asset_condition"]
            + ces * weights["consequence"]
            + cqs * weights["cqs"]
        )
        dhm_multiplier = max(
            self.rules["dhm"]["minimum"],
            min(self.rules["dhm"]["maximum"], base),
        )
        lag_adj = min(
            self.rules["lag"]["maximum_adjustment"],
            (max(0.0, days_overdue) / self.rules["lag"]["days_per_step"])
            * self.rules["lag"]["points_per_step"],
        )
        work_adj = (
            self.rules["scheduled_work_adjustment"]
            if work_already_scheduled
            else 0.0
        )
        score = base * dhm_multiplier + lag_adj + work_adj

        return round(self._clamp(score), 2)
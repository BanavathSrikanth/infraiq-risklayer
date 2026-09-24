from datetime import datetime, timezone
from copy import deepcopy
from uuid import uuid4
from pathlib import Path

from app.application.risk_classification import RiskClassifier
from app.application.risk_explainability import (
    RiskExplainabilityService,
)
from app.application.scoring.ahs import AhsCalculator
from app.application.scoring.ces import CesCalculator
from app.application.scoring.cqs import CqsCalculator
from app.application.scoring.dhm import DhmCalculator
from app.application.scoring.ops import OpsCalculator
from app.application.scoring.ves import VesCalculator

from app.domain.schemas.risk_input import RiskInput
from app.domain.schemas.risk_result import RiskResult


class RiskCalculationService:
    _required_feeds = ("AHS", "CES", "CQS", "DHM", "VES")
    _feed_columns = {
        "AHS": (
            "ahs.age_years",
            "ahs.material",
            "ahs.remaining_fiber_pct",
            "ahs.defect_severity",
            "ahs.lean_deg",
            "ahs.attachment_count",
            "ahs.asset_class",
            "ahs.reinforced_within_10_years",
        ),
        "CES": (
            "ces.hftd_tier",
            "ces.fhsz_level",
            "ces.landfire_ros_class",
            "ces.slope_deg",
            "ces.p95_historical_gust_mps",
        ),
        "CQS": (
            "cqs.population_density_1km",
            "cqs.critical_facilities_2km",
            "cqs.customers_on_circuit_segment",
            "cqs.road_density",
        ),
        "DHM": (
            "weather.wind_speed_mph",
            "weather.temperature_f",
            "weather.relative_humidity_pct",
            "weather.precipitation_in",
            "weather.fire_weather_index",
        ),
        "VES": (
            "ves.proximity_factor",
            "ves.density_factor",
            "ves.clearance_factor",
            "ves.overlap_factor",
            "ves.encroach_factor",
        ),
    }

    def __init__(self, rules_directory: str):
        rules_path = Path(rules_directory)
        if not rules_path.exists():
            rules_path = Path(__file__).parents[1] / "domain" / "rules" / "v1"

        self.ahs_calculator = AhsCalculator(
            str(self._rule_path(rules_path, "ahs"))
        )

        self.ces_calculator = CesCalculator(
            str(self._rule_path(rules_path, "ces"))
        )

        self.cqs_calculator = CqsCalculator(
            str(self._rule_path(rules_path, "cqs"))
        )

        self.dhm_calculator = DhmCalculator(
            str(self._rule_path(rules_path, "dhm"))
        )

        self.ops_calculator = OpsCalculator(
            str(self._rule_path(rules_path, "ops"))
        )

        self.ves_calculator = VesCalculator(
            str(self._rule_path(rules_path, "ves"))
        )

        self.classifier = RiskClassifier(
            str(self._rule_path(rules_path, "risk"))
        )

        self.explainability = RiskExplainabilityService()

        self.calculation_version = self.classifier.rules["version"]

    @staticmethod
    def _rule_path(rules_path: Path, rule_name: str) -> Path:
        yaml_path = rules_path / f"{rule_name}.yaml"
        legacy_path = rules_path / f"{rule_name}.yaml.txt"
        if yaml_path.exists():
            return yaml_path
        if legacy_path.exists():
            return legacy_path
        raise FileNotFoundError(
            f"No rule file found for '{rule_name}' in {rules_path}"
        )

    @staticmethod
    def _clamp_score(score: float) -> float:
        return max(0.0, min(100.0, score))

    def _confidence_and_warnings(self, data: RiskInput) -> tuple[float, list[str]]:
        stale = {feed.upper() for feed in data.stale_feeds}
        imputed = {feed.upper() for feed in data.imputed_feeds}
        missing = {feed.upper() for feed in data.missing_feeds}
        critical_missing = {
            feed.upper() for feed in data.critical_missing_feeds
        }

        confidence = 1.0
        for feed in self._required_feeds:
            if feed in missing:
                factor = 0.3
            elif feed in imputed:
                factor = 0.5
            elif feed in stale:
                factor = 0.8
            else:
                factor = 1.0
            confidence *= factor

        missing_columns = []
        for feed, columns in self._feed_columns.items():
            feed_name, *_ = columns[0].split(".")
            model = getattr(data, feed_name)
            present_fields = model.model_fields_set
            missing_columns.extend(
                column
                for column in columns
                if column.split(".")[1] not in present_fields
            )
        for feed in missing:
            missing_columns.extend(self._feed_columns.get(feed, ()))
        missing_columns = sorted(set(missing_columns))

        warnings = []
        if missing_columns:
            warnings.append(
                "Missing dataset columns: "
                + ", ".join(missing_columns)
            )
        if critical_missing:
            confidence = min(confidence, 0.5)
            warnings.append(
                "Critical input missing: "
                + ", ".join(sorted(critical_missing))
            )

        return round(confidence, 4), warnings

    def calculate(self, data: RiskInput) -> RiskResult:

        calculated_at = (
            data.calculated_at
            or datetime.now(timezone.utc)
        )
        source_captured_at = datetime.now(timezone.utc)
        source_event_id = str(uuid4())

        # Individual risk factors
        ahs = self.ahs_calculator.calculate(data.ahs)

        ces = self.ces_calculator.calculate(
            data.ces
        )

        cqs = self.cqs_calculator.calculate(
            data.cqs
        )

        dhm = self.dhm_calculator.calculate(
            data.weather
        )

        ops = self.ops_calculator.calculate(
            ahs=ahs,
            ces=ces,
            cqs=cqs,
            days_overdue=data.days_overdue,
            work_already_scheduled=data.work_already_scheduled,
        )

        ves = self.ves_calculator.calculate(data.ves)

        # Composite risk
        weights = self.classifier.weights

        risk_score = (
            ahs * weights["ahs"]
            + ces * weights["ces"]
            + cqs * weights["cqs"]
            + ves * weights["ves"]
        )

        risk_score = round(
            self._clamp_score(risk_score),
            2,
        )

        # Classification
        risk_category = self.classifier.classify(
            risk_score
        )
        confidence, warnings = self._confidence_and_warnings(data)

        # Preserve original inputs
        input_values = deepcopy(data.model_dump(mode="json"))

        # Explainability
        explanation = self.explainability.build_explanation(
            ahs=ahs,
            ces=ces,
            cqs=cqs,
            dhm=dhm,
            ops=ops,
            ves=ves,
            weights=weights,
            inputs=input_values,
            calculation_version=self.calculation_version,
            confidence=confidence,
        )

        return RiskResult(
            asset_id=data.asset_id,
            tenant_id=data.tenant_id,
            risk_score=risk_score,
            risk_category=risk_category,
            ahs=ahs,
            ces=ces,
            cqs=cqs,
            dhm=dhm,
            ops=ops,
            ves=ves,
            calculated_at=calculated_at,
            source_captured_at=source_captured_at,
            source_event_id=source_event_id,
            calculation_version=self.calculation_version,
            input_values=input_values,
            explanation=explanation,
            confidence=confidence,
            stale=bool(data.stale_feeds),
            warnings=warnings,
        )
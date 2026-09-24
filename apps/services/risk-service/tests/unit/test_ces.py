from pathlib import Path

from app.application.scoring.ces import CesCalculator
from app.domain.schemas.risk_input import CesInput


def test_ces_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ces.yaml"
    )

    calculator = CesCalculator(str(rules))

    data = CesInput(
        hftd_tier="tier_3",
        fhsz_level="very_high",
        landfire_ros_class=5,
        slope_deg=45,
        p95_historical_gust_mps=30,
    )

    score = calculator.calculate(data)

    assert score == 100.0


def test_ces_uses_environmental_factors_and_configured_weights():
    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ces.yaml"
    )
    calculator = CesCalculator(str(rules))

    score = calculator.calculate(
        CesInput(
            hftd_tier="tier_1",
            fhsz_level="moderate",
            landfire_ros_class=3,
            slope_deg=22.5,
            p95_historical_gust_mps=15,
        )
    )

    assert score == 50.0
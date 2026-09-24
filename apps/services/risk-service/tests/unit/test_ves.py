from pathlib import Path

from app.application.scoring.ves import VesCalculator
from app.domain.schemas.risk_input import VesInput


def test_ves_calculation_uses_configured_weights():
    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ves.yaml"
    )
    calculator = VesCalculator(str(rules))

    score = calculator.calculate(
        VesInput(
            proximity_factor=1.0,
            density_factor=0.5,
            clearance_factor=0.0,
            overlap_factor=1.0,
            encroach_factor=0.5,
        )
    )

    assert score == 45.0

from pathlib import Path

from app.application.scoring.cqs import CqsCalculator
from app.domain.schemas.risk_input import CqsInput


def test_cqs_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "cqs.yaml"
    )

    calculator = CqsCalculator(str(rules))

    data = CqsInput(
        population_density_1km=5_000,
        critical_facilities_2km=10,
        customers_on_circuit_segment=5_000,
        road_density=50,
    )

    score = calculator.calculate(data)

    assert score == 50.0
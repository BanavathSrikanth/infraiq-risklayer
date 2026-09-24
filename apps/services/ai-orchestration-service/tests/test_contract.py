from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_extraction_returns_non_authoritative_proposal_with_provenance():
    response = client.post(
        "/api/v1/extraction/propose",
        json={
            "text": "Visible crack near the base",
            "source_references": [
                {
                    "source_id": "inspection-1",
                    "source_type": "inspection",
                    "locator": "page:2",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["entities"]
    proposal = payload["entities"][0]
    assert proposal["provenance"]["authoritative"] is False
    assert proposal["provenance"]["proposal_status"] == "proposed"
    assert proposal["provenance"]["source_references"][0]["source_id"] == "inspection-1"
    assert proposal["provenance"]["model_name"]
    assert proposal["provenance"]["prompt_id"]
    assert payload["authoritative_record_ids"] == []


def test_recommendation_is_a_proposal_not_a_business_record():
    response = client.post(
        "/api/v1/evaluation/propose",
        json={"text": "Review the high-severity finding"},
    )

    assert response.status_code == 200
    recommendation = response.json()["recommendations"][0]
    assert recommendation["provenance"]["authoritative"] is False

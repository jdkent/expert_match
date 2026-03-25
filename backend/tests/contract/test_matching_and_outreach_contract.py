from app.core.config import DEFAULT_SIMILARITY_THRESHOLD
from tests.helpers import create_expert


def test_match_query_contract(client):
    expert_id = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Reproducible research workflows"],
    )["profile_id"]

    match_response = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "I need help with research workflows",
        },
    )
    assert match_response.status_code == 201
    match_payload = match_response.json()
    assert match_payload["applied_similarity_threshold"] == DEFAULT_SIMILARITY_THRESHOLD
    assert len(match_payload["matches"]) <= 5
    assert match_payload["matches"][0]["expert_id"] == expert_id

    availability_response = client.get(f"/api/v1/experts/{expert_id}/availability")
    slot_id = availability_response.json()[0]["slot_id"]
    assert slot_id

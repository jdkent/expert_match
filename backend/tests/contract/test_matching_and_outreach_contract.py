from tests.helpers import create_expert


def test_match_query_and_outreach_contract(client):
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
    assert match_payload["applied_similarity_threshold"] == 0.5
    assert len(match_payload["matches"]) <= 5

    availability_response = client.get(f"/api/v1/experts/{expert_id}/availability")
    slot_id = availability_response.json()[0]["slot_id"]

    outreach_response = client.post(
        "/api/v1/outreach-requests",
        json={
            "match_query_id": match_payload["match_query_id"],
            "primary_expert_id": expert_id,
            "requester": {"full_name": "Grace Hopper", "email": "grace@example.org"},
            "recipients": [{"expert_id": expert_id, "availability_slot_ids": [slot_id]}],
            "message_body": "Can we talk about reproducible workflows?",
        },
    )
    assert outreach_response.status_code == 201
    assert outreach_response.json()["overall_status"] == "sent"

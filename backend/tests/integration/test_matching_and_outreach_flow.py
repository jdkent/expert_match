from tests.helpers import create_expert


def test_thresholded_search_deduplicates_experts_and_sends_primary_outreach(client):
    assert client.get("/readyz").status_code == 200
    first_expert_id = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=[
            "Reproducible research workflows",
            "Research metadata quality",
        ],
    )["profile_id"]
    second_expert_id = create_expert(
        client,
        full_name="Katherine Johnson",
        email="katherine@example.org",
        expertise_entries=["Orbital mechanics and demonstration planning"],
    )["profile_id"]

    match_response = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "I need advice on research workflows and metadata",
        },
    )
    payload = match_response.json()
    assert len(payload["matches"]) == 2
    returned_ids = [match["expert_id"] for match in payload["matches"]]
    assert returned_ids.count(first_expert_id) == 1
    assert first_expert_id in returned_ids
    assert second_expert_id in returned_ids

    first_slot = client.get(f"/api/v1/experts/{first_expert_id}/availability").json()[0]["slot_id"]
    outreach_response = client.post(
        "/api/v1/outreach-requests",
        json={
            "match_query_id": payload["match_query_id"],
            "primary_expert_id": first_expert_id,
            "requester": {"full_name": "Grace Hopper", "email": "grace@example.org"},
            "recipients": [
              {"expert_id": first_expert_id, "availability_slot_ids": [first_slot]},
              {"expert_id": second_expert_id, "availability_slot_ids": []}
            ],
            "message_body": "I would like to discuss reproducible research workflows.",
        },
    )
    assert outreach_response.status_code == 201
    assert outreach_response.json()["overall_status"] == "sent"


def test_primary_expert_must_be_in_recipients(client):
    assert client.get("/healthz").status_code == 200
    expert_id = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows"],
    )["profile_id"]
    match_payload = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "metadata",
        },
    ).json()
    response = client.post(
        "/api/v1/outreach-requests",
        json={
            "match_query_id": match_payload["match_query_id"],
            "primary_expert_id": "00000000-0000-0000-0000-000000000123",
            "requester": {"full_name": "Grace Hopper", "email": "grace@example.org"},
            "recipients": [{"expert_id": expert_id, "availability_slot_ids": []}],
            "message_body": "hello",
        },
    )
    assert response.status_code == 422

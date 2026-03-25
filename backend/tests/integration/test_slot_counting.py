from tests.helpers import create_expert


def test_repeated_outreach_increments_slot_count_without_locking_slot(client):
    assert client.get("/readyz").status_code == 200
    expert = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows"],
    )
    expert_id = expert["profile_id"]
    match_payload = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "metadata workflows",
        },
    ).json()
    slot_id = client.get(f"/api/v1/experts/{expert_id}/availability").json()[0]["slot_id"]

    for requester_name in ("Grace Hopper", "Alan Turing"):
        response = client.post(
            "/api/v1/outreach-requests",
            json={
                "match_query_id": match_payload["match_query_id"],
                "primary_expert_id": expert_id,
                "requester": {
                    "full_name": requester_name,
                    "email": f"{requester_name.split()[0].lower()}@example.org",
                },
                "recipients": [{"expert_id": expert_id, "availability_slot_ids": [slot_id]}],
                "message_body": "Can we meet?",
            },
        )
        assert response.status_code == 201

    updated_slot = client.get(f"/api/v1/experts/{expert_id}/availability").json()[0]
    assert updated_slot["attendee_request_count"] == 2
    assert updated_slot["is_available"] is True


def test_editing_profile_preserves_existing_slot_demand_counts(client):
    expert = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows"],
    )
    expert_id = expert["profile_id"]
    match_payload = client.post(
        "/api/v1/match-queries",
        json={"query_text": "metadata workflows"},
    ).json()
    slot_id = client.get(f"/api/v1/experts/{expert_id}/availability").json()[0]["slot_id"]
    outreach_response = client.post(
        "/api/v1/outreach-requests",
        json={
            "match_query_id": match_payload["match_query_id"],
            "primary_expert_id": expert_id,
            "requester": {
                "full_name": "Grace Hopper",
                "email": "grace@example.org",
            },
            "recipients": [{"expert_id": expert_id, "availability_slot_ids": [slot_id]}],
            "message_body": "Can we meet?",
        },
    )
    assert outreach_response.status_code == 201

    patch_response = client.patch(
        "/api/v1/expert-access/profile",
        json={
            "access_key": expert["access_key"],
            "expertise_entries": ["Metadata workflows", "ORCID support"],
        },
    )
    assert patch_response.status_code == 202

    updated_slot = client.get(f"/api/v1/experts/{expert_id}/availability").json()[0]
    assert updated_slot["attendee_request_count"] == 1

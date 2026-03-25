from tests.helpers import create_expert


def test_outreach_without_slots_is_allowed(client):
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
    availability = client.get(f"/api/v1/experts/{expert_id}/availability").json()
    client.patch(
        "/api/v1/expert-access/profile",
        json={"access_key": expert["access_key"], "available_slot_ids": []},
    )
    response = client.post(
        "/api/v1/outreach-requests",
        json={
            "match_query_id": match_payload["match_query_id"],
            "primary_expert_id": expert_id,
            "requester": {"full_name": "Grace Hopper", "email": "grace@example.org"},
            "recipients": [{"expert_id": expert_id, "availability_slot_ids": []}],
            "message_body": "Can we connect later?",
        },
    )
    assert response.status_code == 201
    assert len(availability) == 180

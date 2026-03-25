from tests.helpers import create_expert


def test_availability_contract_returns_canonical_slots(client):
    expert_id = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows"],
    )["profile_id"]

    response = client.get(f"/api/v1/experts/{expert_id}/availability")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 180
    assert all("slot_id" in slot for slot in payload)

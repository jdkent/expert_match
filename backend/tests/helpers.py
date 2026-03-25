from fastapi.testclient import TestClient


def create_expert(
    client: TestClient,
    *,
    full_name: str,
    email: str,
    expertise_entries: list[str],
    orcid_id: str | None = None,
    available_slot_ids: list[str] | None = None,
):
    response = client.post(
        "/api/v1/experts",
        json={
            "full_name": full_name,
            "email": email,
            "orcid_id": orcid_id,
            "expertise_entries": expertise_entries,
            "available_slot_ids": available_slot_ids,
        },
    )
    assert response.status_code == 202
    client.app.state.services["expert_profile"].wait_for_idle(timeout=120)
    return response.json()

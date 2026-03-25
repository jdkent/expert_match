import pytest

def test_health_and_readiness_endpoints_use_shared_runtime_contract(client):
    health_response = client.get("/healthz")
    ready_response = client.get("/readyz")

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"


@pytest.mark.vcr
def test_expert_submission_access_key_edit_and_deletion_flow(client):
    create_response = client.post(
        "/api/v1/experts",
        json={
            "full_name": "Russell Poldrack",
            "email": "ada@example.org",
            "short_bio": "Cognitive neuroscientist focused on reproducible neuroimaging methods.",
            "orcid_id": "0000-0001-6755-0259",
            "website_url": "https://ada.example.org",
            "expertise_entries": ["Metadata workflows", "Publication cleanup"],
        },
    )
    assert create_response.status_code == 202
    access_key = create_response.json()["access_key"]
    client.app.state.services["expert_profile"].wait_for_idle(timeout=120)

    profile_response = client.post(
        "/api/v1/expert-access/profile",
        json={"access_key": access_key},
    )
    assert profile_response.json()["short_bio"] == "Cognitive neuroscientist focused on reproducible neuroimaging methods."
    assert profile_response.json()["orcid_id"] == "0000-0001-6755-0259"
    assert len(profile_response.json()["availability_slots"]) == 180

    chosen_slot_ids = [
        slot["slot_id"] for slot in profile_response.json()["availability_slots"][:2]
    ]
    patch_response = client.patch(
        "/api/v1/expert-access/profile",
        json={
            "access_key": access_key,
            "short_bio": "Neuroimaging methods expert and open science advocate.",
            "expertise_entries": ["Metadata workflows", "ORCID adoption"],
            "available_slot_ids": chosen_slot_ids,
        },
    )
    assert patch_response.status_code == 202
    client.app.state.services["expert_profile"].wait_for_idle(timeout=120)

    updated_profile = client.post(
        "/api/v1/expert-access/profile",
        json={"access_key": access_key},
    ).json()
    assert updated_profile["short_bio"] == "Neuroimaging methods expert and open science advocate."
    assert updated_profile["expertise_entries"] == ["Metadata workflows", "ORCID adoption"]
    assert sum(1 for slot in updated_profile["availability_slots"] if slot["is_available"]) == 2

    match_response = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "ORCID adoption",
        },
    )
    assert match_response.status_code == 201
    assert match_response.json()["matches"][0]["short_bio"] == "Neuroimaging methods expert and open science advocate."

    delete_response = client.request(
        "DELETE",
        "/api/v1/expert-access/profile",
        json={"access_key": access_key, "email_confirmation": "ada@example.org"},
    )
    assert delete_response.status_code == 202

    post_delete_match_response = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "ORCID adoption",
        },
    )
    assert post_delete_match_response.json()["matches"] == []


def test_duplicate_submission_requires_existing_access_key(client):
    first_response = client.post(
        "/api/v1/experts",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.org",
            "expertise_entries": ["Metadata workflows"],
        },
    )
    first_profile_id = first_response.json()["profile_id"]
    client.app.state.services["expert_profile"].wait_for_idle(timeout=120)
    second_response = client.post(
        "/api/v1/experts",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.org",
            "expertise_entries": ["Research software"],
        },
    )
    assert second_response.status_code == 409
    assert first_profile_id

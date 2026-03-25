from tests.helpers import create_expert


def test_create_and_edit_profile_contract(client):
    create_response = client.post(
        "/api/v1/experts",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.org",
            "expertise_entries": ["Metadata workflows"],
        },
    )
    assert create_response.status_code == 202
    create_payload = create_response.json()
    assert "profile_id" in create_payload
    assert "access_key" in create_payload

    get_response = client.post(
        "/api/v1/expert-access/profile",
        json={"access_key": create_payload["access_key"]},
    )
    assert get_response.status_code == 200
    assert get_response.json()["email"] == "ada@example.org"

    patch_response = client.patch(
        "/api/v1/expert-access/profile",
        json={
            "access_key": create_payload["access_key"],
            "expertise_entries": ["Metadata workflows", "ORCID support"],
        },
    )
    assert patch_response.status_code == 202


def test_delete_profile_requires_confirmation(client):
    create_payload = create_expert(
        client,
        full_name="Delete Me",
        email="delete@example.org",
        expertise_entries=["Expert topic"],
    )

    bad_delete = client.request(
        "DELETE",
        "/api/v1/expert-access/profile",
        json={
            "access_key": create_payload["access_key"],
            "email_confirmation": "wrong@example.org",
        },
    )
    assert bad_delete.status_code == 422

from tests.helpers import create_expert


def test_thresholded_search_deduplicates_experts(client):
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
        expertise_entries=["Research workflow planning for metadata-heavy demos"],
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

def test_match_query_does_not_require_outreach_payload(client):
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
    assert match_payload["match_query_id"]
    assert match_payload["matches"][0]["expert_id"] == expert_id

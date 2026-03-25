import httpx

from app.scripts.ingest_methods_neuroscientists import ingest_expert, run
from app.seed_data import METHODS_NEUROSCIENTIST_EXPERTS


def test_ingest_expert_skips_existing_profiles():
    expert = METHODS_NEUROSCIENTIST_EXPERTS[0]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/experts"
        return httpx.Response(
            409,
            json={
                "detail": "A profile already exists for this email address; use the expert access key to update it.",
            },
        )

    client = httpx.Client(base_url="http://localhost:8000", transport=httpx.MockTransport(handler))
    try:
        profile_id, access_key, created = ingest_expert(client, expert)
    finally:
        client.close()

    assert profile_id is None
    assert access_key is None
    assert created is False


def test_run_reports_seeded_and_skipped_counts(capsys):
    expert = METHODS_NEUROSCIENTIST_EXPERTS[0]
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(
                202,
                json={"profile_id": "profile-123", "access_key": "access-123"},
            )
        return httpx.Response(
            409,
            json={
                "detail": "A profile already exists for this email address; use the expert access key to update it.",
            },
        )

    transport = httpx.MockTransport(handler)
    original = METHODS_NEUROSCIENTIST_EXPERTS[:2]

    class FakeClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, transport=transport, **kwargs)

    from app.scripts import ingest_methods_neuroscientists as module

    original_client = module.httpx.Client
    original_seed = module.METHODS_NEUROSCIENTIST_EXPERTS
    module.httpx.Client = FakeClient
    module.METHODS_NEUROSCIENTIST_EXPERTS = original
    try:
        assert run("http://localhost:8000", limit=2, timeout_seconds=1.0) == 0
    finally:
        module.httpx.Client = original_client
        module.METHODS_NEUROSCIENTIST_EXPERTS = original_seed

    output = capsys.readouterr().out
    assert f"seeded {expert.full_name}" in output
    assert "reason=profile already exists" in output
    assert "completed ingestion for 2 experts (seeded=1, skipped=1)" in output

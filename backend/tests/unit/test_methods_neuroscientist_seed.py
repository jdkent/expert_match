from app.seed_data import METHODS_NEUROSCIENTIST_EXPERTS


def test_curated_methods_seed_has_twenty_unique_experts():
    assert len(METHODS_NEUROSCIENTIST_EXPERTS) == 20
    assert len({expert.email for expert in METHODS_NEUROSCIENTIST_EXPERTS}) == 20
    assert len({expert.orcid_id for expert in METHODS_NEUROSCIENTIST_EXPERTS}) == 20
    assert all(expert.source_url == f"https://orcid.org/{expert.orcid_id}" for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(len(expert.expertise_entries) >= 3 for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(expert.website_url.startswith("https://profiles.seeded-experts.dev/") for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(expert.x_handle for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(expert.linkedin_identifier for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(expert.bluesky_identifier.endswith(".seeded-experts.dev") for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(expert.github_handle.endswith("-lab") for expert in METHODS_NEUROSCIENTIST_EXPERTS)

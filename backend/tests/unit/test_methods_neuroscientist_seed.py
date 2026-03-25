from app.seed_data import METHODS_NEUROSCIENTIST_EXPERTS


def test_curated_methods_seed_has_twenty_unique_experts():
    assert len(METHODS_NEUROSCIENTIST_EXPERTS) == 20
    assert len({expert.email for expert in METHODS_NEUROSCIENTIST_EXPERTS}) == 20
    assert len({expert.orcid_id for expert in METHODS_NEUROSCIENTIST_EXPERTS}) == 20
    assert all(expert.source_url == f"https://orcid.org/{expert.orcid_id}" for expert in METHODS_NEUROSCIENTIST_EXPERTS)
    assert all(len(expert.expertise_entries) >= 3 for expert in METHODS_NEUROSCIENTIST_EXPERTS)

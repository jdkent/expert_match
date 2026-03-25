import pytest

from app.core.config import Settings
from app.services.openalex_client import OpenAlexClient


KNOWN_METHODS_ORCID = "0000-0001-6755-0259"
MISSING_ORCID = "0000-0000-0000-0000"


@pytest.mark.vcr
def test_lookup_recent_publications_prioritizes_primary_authorship():
    client = OpenAlexClient(
        settings=Settings(
            openalex_enabled=True,
            openalex_email="jamesdkent21@gmail.com",
            openalex_base_url="https://api.openalex.org",
        )
    )

    publications = client.lookup_recent_publications(KNOWN_METHODS_ORCID, max_results=3)

    assert len(publications) == 3
    assert all(publication["author_priority"] == "primary" for publication in publications)
    assert publications == sorted(
        publications,
        key=lambda publication: publication["publication_date"],
        reverse=True,
    )
    assert all(publication["abstract_text"] for publication in publications)


@pytest.mark.vcr
def test_lookup_recent_publications_returns_empty_when_author_is_missing():
    client = OpenAlexClient(
        settings=Settings(
            openalex_enabled=True,
            openalex_email="jamesdkent21@gmail.com",
            openalex_base_url="https://api.openalex.org",
        )
    )

    assert client.lookup_recent_publications(MISSING_ORCID) == []

import pytest

from app.core.config import Settings
from app.services.orcid_client import OrcidClient


KNOWN_METHODS_ORCID = "0000-0001-6755-0259"
MISSING_ORCID = "0000-0000-0000-0000"


def test_validate_orcid_checks_shape():
    client = OrcidClient(settings=Settings(orcid_live_validation=True))

    assert client.validate_orcid(KNOWN_METHODS_ORCID) is True
    assert client.validate_orcid("not-an-orcid") is False


@pytest.mark.vcr
def test_record_exists_uses_real_orcid_record_lookup():
    client = OrcidClient(
        settings=Settings(
            orcid_live_validation=True,
            orcid_base_url="https://pub.orcid.org/v3.0",
        )
    )

    assert client.record_exists(KNOWN_METHODS_ORCID) is True
    assert client.record_exists(MISSING_ORCID) is False

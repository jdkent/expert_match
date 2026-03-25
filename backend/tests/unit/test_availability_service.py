import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.db.session import get_session_factory
from app.models.expert_profile import ExpertProfile
from app.services.availability_service import AvailabilityService


def test_initialize_defaults_all_slots_available(session_factory):
    service = AvailabilityService(session_factory=session_factory)
    availability = service.initialize_for_profile("00000000-0000-0000-0000-000000000111")
    assert len(availability) == 180
    assert all(slot.is_available for slot in availability)


def test_unknown_slot_raises(session_factory):
    profile_id = "00000000-0000-0000-0000-000000000222"
    with session_factory() as session:
        session.add(
            ExpertProfile(
                id=profile_id,
                full_name="Ada Lovelace",
                email="ada@example.org",
                orcid_id=None,
                website_url=None,
                x_handle=None,
                linkedin_identifier=None,
                bluesky_identifier=None,
                github_handle=None,
                orcid_validation_status="not_provided",
                discoverability_status="active",
                access_key_hash="dummy",
            )
        )
        session.commit()
    service = AvailabilityService(session_factory=session_factory)
    with pytest.raises(HTTPException):
        service.get_slot(profile_id, "00000000-0000-0000-0000-000000009999")


def test_session_factory_requires_database_configuration():
    with pytest.raises(RuntimeError):
        get_session_factory(Settings(POSTGRES_DSN=None))

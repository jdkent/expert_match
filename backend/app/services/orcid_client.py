import re

import httpx

from app.core.config import Settings
from app.core.logging import logger


ORCID_PATTERN = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


class OrcidClient:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        settings = settings or Settings()
        self.base_url = settings.orcid_base_url.rstrip("/")
        self.live_validation = settings.orcid_live_validation
        self.timeout_seconds = settings.orcid_timeout_seconds
        self.transport = transport

    def validate_orcid(self, orcid_id: str | None) -> bool:
        if orcid_id is None:
            return True
        return bool(ORCID_PATTERN.fullmatch(orcid_id.strip()))

    def record_exists(self, orcid_id: str) -> bool:
        if not self.validate_orcid(orcid_id):
            return False
        if not self.live_validation:
            return True
        try:
            with httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                transport=self.transport,
                headers={"Accept": "application/json"},
            ) as client:
                response = client.get(f"/{orcid_id}/person")
                if response.status_code == 404:
                    return False
                response.raise_for_status()
            return True
        except httpx.HTTPError as exc:
            logger.warning("ORCID lookup failed for %s: %s", orcid_id, exc)
            return False

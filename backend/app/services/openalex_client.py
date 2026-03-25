from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.core.config import Settings
from app.core.logging import logger


class OpenAlexClient:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        settings = settings or Settings()
        self.base_url = settings.openalex_base_url.rstrip("/")
        self.enabled = settings.openalex_enabled
        self.mailto = settings.openalex_email
        self.api_key = settings.openalex_api_key
        self.timeout_seconds = settings.openalex_timeout_seconds
        self.transport = transport

    def lookup_recent_publications(self, orcid_id: str, max_results: int = 25) -> list[dict]:
        if not self.enabled:
            return []
        try:
            author_id = self._lookup_author_id(orcid_id)
            if author_id is None:
                return []
            works = self._lookup_works(author_id=author_id, max_results=max_results)
            return self._serialize_works(works=works, author_id=author_id, max_results=max_results)
        except httpx.HTTPError as exc:
            logger.warning("OpenAlex lookup failed for %s: %s", orcid_id, exc)
            return []

    def _lookup_author_id(self, orcid_id: str) -> str | None:
        response = self._request(
            "/authors",
            params={"filter": f"orcid:https://orcid.org/{orcid_id}"},
        )
        results = response.json().get("results", [])
        if not results:
            return None
        return results[0]["id"]

    def _lookup_works(self, *, author_id: str, max_results: int) -> list[dict[str, Any]]:
        response = self._request(
            "/works",
            params={
                "filter": f"author.id:{author_id}",
                "sort": "publication_date:desc",
                "per-page": str(min(max(max_results * 4, max_results), 100)),
                "select": "id,display_name,publication_date,abstract_inverted_index,authorships",
            },
        )
        return response.json().get("results", [])

    def _request(self, path: str, *, params: dict[str, str]) -> httpx.Response:
        query_params = dict(params)
        if self.mailto:
            query_params["mailto"] = self.mailto
        if self.api_key:
            query_params["api_key"] = self.api_key
        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            response = client.get(path, params=query_params)
            response.raise_for_status()
            return response

    def _serialize_works(self, *, works: list[dict[str, Any]], author_id: str, max_results: int) -> list[dict]:
        primary: list[dict] = []
        secondary: list[dict] = []
        for work in works:
            authorship = self._matching_authorship(work.get("authorships") or [], author_id)
            if authorship is None:
                continue
            serialized = {
                "external_work_id": work["id"],
                "title": work.get("display_name") or "Untitled work",
                "publication_date": self._parse_date(work.get("publication_date")),
                "author_position": authorship["author_position"],
                "author_priority": (
                    "primary" if authorship["author_position"] in {"first", "last"} else "secondary"
                ),
                "abstract_text": self._reconstruct_abstract(work.get("abstract_inverted_index")),
                "abstract_status": (
                    "present" if work.get("abstract_inverted_index") else "missing"
                ),
            }
            if serialized["author_priority"] == "primary":
                primary.append(serialized)
            else:
                secondary.append(serialized)
        ranked = sorted(
            primary,
            key=lambda item: item["publication_date"] or date.min,
            reverse=True,
        )
        if len(ranked) < max_results:
            ranked.extend(
                sorted(
                    secondary,
                    key=lambda item: item["publication_date"] or date.min,
                    reverse=True,
                )[: max_results - len(ranked)]
            )
        return ranked[:max_results]

    @staticmethod
    def _matching_authorship(authorships: list[dict[str, Any]], author_id: str) -> dict[str, Any] | None:
        for authorship in authorships:
            author = authorship.get("author") or {}
            if author.get("id") == author_id:
                return authorship
        return None

    @staticmethod
    def _parse_date(raw_value: str | None) -> date | None:
        if not raw_value:
            return None
        try:
            return date.fromisoformat(raw_value)
        except ValueError:
            return None

    @staticmethod
    def _reconstruct_abstract(abstract_inverted_index: dict[str, list[int]] | None) -> str | None:
        if not abstract_inverted_index:
            return None
        max_position = max(position for positions in abstract_inverted_index.values() for position in positions)
        tokens = [""] * (max_position + 1)
        for token, positions in abstract_inverted_index.items():
            for position in positions:
                tokens[position] = token
        return " ".join(token for token in tokens if token).strip() or None

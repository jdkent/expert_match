from __future__ import annotations

from uuid import uuid4

from app.models.enums import EnrichmentStatus


class ExpertEnrichmentWorker:
    def run(self, service, *, profile, trigger_source: str, available_slot_ids):
        run = {
            "id": uuid4(),
            "trigger_source": trigger_source,
            "status": EnrichmentStatus.RUNNING.value,
            "publication_selected_count": 0,
            "publication_embedded_count": 0,
            "availability_initialized": False,
            "last_error": None,
        }
        profile.enrichment_runs.append(run)
        try:
            service.refresh_search_documents(profile, available_slot_ids=available_slot_ids)
            run["publication_selected_count"] = len(profile.publications)
            run["publication_embedded_count"] = sum(
                1
                for document in profile.search_documents
                if document["source_type"] == "publication_abstract"
            )
            run["availability_initialized"] = True
            run["status"] = EnrichmentStatus.COMPLETED.value
        except Exception as exc:  # pragma: no cover - defensive path
            run["status"] = EnrichmentStatus.FAILED.value
            run["last_error"] = str(exc)
            raise

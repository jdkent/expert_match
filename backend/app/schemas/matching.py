from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import APIModel

class MatchQueryInput(BaseModel):
    query_text: str


class MatchedExpertSummary(APIModel):
    expert_id: UUID
    full_name: str
    email: str
    short_bio: str | None = None
    aggregate_similarity_score: float
    matched_document_excerpt: str
    website_url: str | None = None
    x_handle: str | None = None
    linkedin_identifier: str | None = None
    bluesky_identifier: str | None = None
    github_handle: str | None = None


class MatchQueryResponse(APIModel):
    match_query_id: UUID
    applied_match_acceptance_threshold: float
    matches: list[MatchedExpertSummary]

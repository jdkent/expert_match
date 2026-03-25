from enum import StrEnum


class OrcidValidationStatus(StrEnum):
    NOT_PROVIDED = "not_provided"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class DiscoverabilityStatus(StrEnum):
    PENDING_ENRICHMENT = "pending_enrichment"
    ACTIVE = "active"
    NEEDS_CORRECTION = "needs_correction"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class SourceType(StrEnum):
    MANUAL_EXPERTISE = "manual_expertise"
    PUBLICATION_ABSTRACT = "publication_abstract"


class AuthorPosition(StrEnum):
    FIRST = "first"
    MIDDLE = "middle"
    LAST = "last"


class AuthorPriority(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class AbstractStatus(StrEnum):
    PRESENT = "present"
    MISSING = "missing"
    RETRIEVAL_FAILED = "retrieval_failed"


class EnrichmentTriggerSource(StrEnum):
    INITIAL_SUBMISSION = "initial_submission"
    EXPERT_EDIT = "expert_edit"


class EnrichmentStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL_FAILED = "partial_failed"
    FAILED = "failed"


class SearchStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class OutreachStatus(StrEnum):
    DRAFT = "draft"
    SENDING = "sending"
    PARTIALLY_SENT = "partially_sent"
    SENT = "sent"
    CLOSED = "closed"
    FAILED = "failed"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DECLINED = "declined"
    COMPLETED = "completed"

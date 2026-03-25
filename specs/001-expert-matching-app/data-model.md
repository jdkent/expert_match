# Data Model: Expert Matching and Outreach

## ExpertProfile

**Purpose**: Stores a discoverable expert's identity, contact information, intake
status, and enrichment status.

**Fields**:

- `id`: UUID, primary key
- `full_name`: string, required
- `email`: string, required, unique, normalized to lowercase
- `orcid_id`: string, optional, unique when present
- `website_url`: string, optional
- `x_handle`: string, optional
- `linkedin_identifier`: string, optional
- `bluesky_identifier`: string, optional
- `github_handle`: string, optional
- `email_verification_status`: enum (`pending`, `verified`, `expired`)
- `orcid_validation_status`: enum (`not_provided`, `pending`, `verified`, `failed`)
- `discoverability_status`: enum (`pending_email_verification`, `pending_enrichment`,
  `active`, `needs_correction`, `inactive`, `archived`)
- `created_at`: timestamp
- `updated_at`: timestamp
- `verified_at`: timestamp, nullable

**Relationships**:

- One `ExpertProfile` has many `ExpertiseEntry` records.
- One `ExpertProfile` has many `PublicationRecord` records.
- One `ExpertProfile` has many `ExpertSearchDocument` records.
- One `ExpertProfile` has many `ExpertAvailabilitySlot` records.
- One `ExpertProfile` has many `ExpertEditSession` records.
- One `ExpertProfile` has many `ExpertEnrichmentRun` records.

**Validation rules**:

- Public profile links are optional and independently nullable.
- `website_url`, when present, must be a valid absolute URL.

## ExpertEditSession

**Purpose**: Stores one-time email-based recovery sessions for editing expert profile
fields without requiring an account.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `token_hash`: string, required
- `status`: enum (`pending`, `used`, `expired`, `revoked`)
- `expires_at`: timestamp
- `sent_at`: timestamp
- `used_at`: timestamp, nullable

**Validation rules**:

- The session is created only after an exact email lookup for a known expert profile.
- Tokens must be single-use and stored as hashes.
- A valid session may update `full_name`, `orcid_id`, `expertise_entries`, and
  public profile links plus canonical availability in one submission.
- Profile deletion through the session requires a confirmation email string that
  exactly matches the normalized email on the expert profile before the delete
  operation is accepted.
- Successful deletion cascades removal of the expert profile from active discovery
  data, including expertise entries, search documents, publications, and
  availability rows.

## ExpertiseEntry

**Purpose**: Stores one manually entered expertise item for an expert.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `entry_text`: text, required
- `entry_order`: integer, required
- `is_active`: boolean, default `true`

**Validation rules**:

- A discoverable expert must always have at least one active `ExpertiseEntry`.
- Expert-edit submissions replace the active expertise set with the submitted ordered
  list so additions and removals are modeled by activate or deactivate transitions.

## PublicationRecord

**Purpose**: Stores publication metadata harvested for an ORCID-validated expert.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `external_work_id`: string, required
- `title`: string, required
- `publication_date`: date, nullable
- `author_position`: enum (`first`, `middle`, `last`)
- `author_priority`: enum (`primary`, `secondary`)
- `abstract_text`: text, nullable
- `abstract_status`: enum (`present`, `missing`, `retrieval_failed`)
- `selected_for_enrichment`: boolean, required
- `is_active`: boolean, default `true`

**Validation rules**:

- When an expert updates their ORCID ID, prior ORCID-derived publication records are
  deactivated or replaced as part of the new enrichment run.

## ExpertSearchDocument

**Purpose**: Stores one searchable text unit linked to an expert and its embedding.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `source_type`: enum (`manual_expertise`, `publication_abstract`)
- `source_record_id`: UUID, required
- `document_text`: text, required
- `embedding_vector`: vector, required
- `embedding_model`: string, required, fixed to `allenai/specter2`
- `is_active`: boolean, default `true`

**Validation rules**:

- Search documents derived from replaced expertise entries or superseded ORCID
  publications are deactivated before new expert edits become discoverable.

## ExpertAvailabilitySlot

**Purpose**: Stores one canonical OHBM 2026 Bordeaux availability slot for a specific expert.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `slot_start_at`: timestamp, required
- `slot_end_at`: timestamp, required
- `timezone`: string, required, fixed to `Europe/Paris`
- `local_date`: date, required
- `local_start_time`: time, required
- `is_available`: boolean, required
- `attendee_request_count`: integer, default `0`

**Validation rules**:

- Slots are only valid for June 14, 2026 through June 18, 2026.
- If an expert provides no explicit availability preferences, all canonical slots are
  initialized with `is_available=true`.
- `attendee_request_count` must never be negative.

## ExpertEnrichmentRun

**Purpose**: Tracks asynchronous validation, publication harvesting, embedding work,
and default availability initialization for a submitted or edited expert profile.

**Fields**:

- `id`: UUID, primary key
- `expert_profile_id`: foreign key to `ExpertProfile`
- `trigger_source`: enum (`initial_submission`, `expert_edit`)
- `status`: enum (`pending`, `running`, `completed`, `partial_failed`, `failed`)
- `publication_selected_count`: integer, default `0`
- `publication_embedded_count`: integer, default `0`
- `availability_initialized`: boolean, default `false`
- `last_error`: text, nullable

## RequesterContact

**Purpose**: Captures the person asking the question so experts can reply.

**Fields**:

- `id`: UUID, primary key
- `full_name`: string, required
- `email`: string, required
- `organization`: string, optional

## ExpertQuery

**Purpose**: Stores a requester's free-text question and the embedding used to search
for experts.

**Fields**:

- `id`: UUID, primary key
- `requester_contact_id`: foreign key to `RequesterContact`
- `query_text`: text, required
- `query_embedding_vector`: vector, required after embedding completes
- `embedding_model`: string, required, fixed to `allenai/specter2`
- `similarity_threshold`: decimal, required, default `0.5`
- `search_status`: enum (`pending`, `ready`, `failed`)

## MatchResult

**Purpose**: Persists ranked expert matches for a query so the UI can show results
and explain which source document drove the expert ranking.

**Fields**:

- `id`: UUID, primary key
- `expert_query_id`: foreign key to `ExpertQuery`
- `expert_profile_id`: foreign key to `ExpertProfile`
- `expert_search_document_id`: foreign key to `ExpertSearchDocument`
- `rank_position`: integer, required
- `expert_similarity_score`: decimal, required
- `top_document_similarity_score`: decimal, required
- `match_explanation`: text, optional

**Validation rules**:

- Each `ExpertQuery` may have at most 5 persisted `MatchResult` rows.
- Each `ExpertProfile` may appear at most once per `ExpertQuery`.
- Persisted matches must satisfy the query's `similarity_threshold`.

## OutreachRequest

**Purpose**: Represents a requester's outreach action after selecting one or more
experts from the ranked results.

**Fields**:

- `id`: UUID, primary key
- `expert_query_id`: foreign key to `ExpertQuery`
- `requester_contact_id`: foreign key to `RequesterContact`
- `primary_expert_profile_id`: foreign key to `ExpertProfile`
- `message_subject`: string, required
- `message_body`: text, required
- `overall_status`: enum (`draft`, `sending`, `partially_sent`, `sent`, `closed`,
  `failed`)

**Validation rules**:

- `primary_expert_profile_id` must reference one of the selected outreach recipients.

## OutreachRecipient

**Purpose**: Tracks outreach delivery for each selected expert.

**Fields**:

- `id`: UUID, primary key
- `outreach_request_id`: foreign key to `OutreachRequest`
- `expert_profile_id`: foreign key to `ExpertProfile`
- `delivery_status`: enum (`pending`, `sent`, `failed`, `declined`, `completed`)
- `delivery_reference`: string, optional

**Validation rules**:

- A recipient may have zero selected slots when the expert has no availability or the
  requester chooses not to propose times.
- No more than 5 recipients may be attached to one `OutreachRequest`.

## OutreachRecipientSlot

**Purpose**: Links one outreach recipient to one selected availability slot.

**Fields**:

- `id`: UUID, primary key
- `outreach_recipient_id`: foreign key to `OutreachRecipient`
- `expert_availability_slot_id`: foreign key to `ExpertAvailabilitySlot`

**Validation rules**:

- A recipient may reference multiple slots.
- Sending the outreach increments `attendee_request_count` for each linked slot.

# Feature Specification: Expert Matching and Outreach

**Feature Branch**: `001-expert-matching-app`  
**Created**: 2026-03-24  
**Status**: Draft  
**Input**: User description: "I am building a simple online application where there are
two workflows. 1) people can insert their name/email/orcidID(and/or a description of
their expertise that they want to talk about). that will be stored and become
queryable. 2) people can put in a free text query that is embedded and found most
similar to the top people that could answer that question based on their expertise.
The person selects the person/people and their question is formatted into an email
that will be sent to that person with some sort of scheduling mechanism so the person
asking the query and the expert can identify a time that works best for them to
meet." Additional planning detail: there are no accounts or logins, expert profile
submission is an unauthenticated POST with email validation and optional ORCID
validation, ORCID-linked publications are harvested and abstract embeddings are stored
per publication, multiple expertise entries are stored separately per expert, the
database must have backups, expert availability is managed as 15-minute slots in
Bordeaux time from June 14, 2026 through June 18, 2026, experts can later recover
their profile editor by entering their email on the platform, the one-time edit link
can update availability, ORCID ID, expertise entries, optional public profile links,
or permanently delete the profile after email confirmation, requesters may contact
experts even when no availability is offered, results use a cosine similarity
threshold that starts at 0.5 and returns at most 5 distinct experts, the workflow is
primarily designed around choosing one preferred expert, and requesters may choose
multiple timeslots per outreach."

## Clarifications

### Session 2026-03-24

- Q: Which deployment architecture should v1 target for 10-3000 users? → A: Run `frontend + backend` on one EC2 host with Docker Compose, and use managed PostgreSQL separately.
- Q: Can local Docker Compose include PostgreSQL while still following good AWS deployment practice? → A: Yes. Use a local Compose PostgreSQL service with named-volume persistence for development and testing, but keep AWS production PostgreSQL as a separately managed service instead of running it inside the EC2 Compose stack.
- Q: How close should dev/test and production builds be? → A: Keep the same service boundaries, environment variables, and `/api` routing shape across environments, but allow a development-focused frontend runtime for local iteration while production uses built static assets behind a reverse proxy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish and Edit Expert Profile (Priority: P1)

As a potential expert, I want to submit my contact information, one or more
expertise entries, optional public profile links, and optional OHBM 2026 Bordeaux
availability without creating an account, and later recover my profile editor by
entering my email, so that people with relevant questions can find and contact me or
I can remove my profile if I no longer want to be listed.

**Why this priority**: The application has no value until there is a searchable pool
of experts and a low-friction way for them to keep their availability current.

**Independent Test**: Submit a valid expert profile without authentication, verify the
email address through a one-time link, then later enter the same email to receive an
expert-edit link and confirm that the profile can update ORCID ID, add or remove
expertise entries, update public profile links, delete the profile after reconfirming
the email address, and keep the correct default or edited event availability when the
profile is retained.

**Acceptance Scenarios**:

1. **Given** a visitor has a name, email address, and at least one expertise entry,
   **When** they submit their expert profile without logging in, **Then** the system
   stores the submission, sends a verification message to the provided email address,
   and keeps the profile out of search results until verification succeeds.
2. **Given** a visitor does not explicitly change any availability slots, **When** the
   expert profile is verified, **Then** the system marks the expert as available for
   every 15-minute slot with start times from 08:00 through 16:45 Bordeaux time on
   June 14, 2026 through June 18, 2026.
3. **Given** an expert later enters their exact email address into the expert-edit
   lookup flow, **When** the system finds a matching profile, **Then** the system
   sends an email-based edit link that allows the expert to update ORCID ID,
   expertise entries, optional public profile links, and availability without
   creating an account.
4. **Given** an expert uses a valid one-time edit link and chooses to delete their
   profile, **When** they re-enter the same email address as an irreversible
   confirmation, **Then** the system permanently removes the expert profile from
   discovery and rejects later attempts to restore it through the product workflow.

---

### User Story 2 - Find and Contact Relevant Experts (Priority: P2)

As a person with a question, I want to describe my need in free text, review a small
set of the best distinct expert matches, and choose a preferred expert plus optional
backup experts while drafting outreach so that I can contact the right person even
when availability is limited.

**Why this priority**: Matching requesters to the right people is the main user value
of the application once expert profiles exist.

**Independent Test**: Submit a question, review up to 5 distinct matched experts that
clear the similarity threshold, choose one preferred expert and optionally additional
experts, select multiple availability slots for an expert who offers them, and
confirm that outreach can still be sent without timeslots to an expert who has no
active availability.

**Acceptance Scenarios**:

1. **Given** discoverable expert profiles exist, **When** a requester enters a free
   text question, **Then** the system returns up to 5 distinct experts whose
   aggregated similarity scores meet the configured cosine threshold, even if many of
   the highest-scoring documents belong to the same expert.
2. **Given** a ranked list of experts is shown, **When** the requester selects one or
   more experts, **Then** the system shows profile context including optional website
   and social links plus currently available OHBM 2026 Bordeaux slots for each selected
   expert, including how many meetings are already requested for each slot.
3. **Given** a requester is preparing outreach, **When** they choose one expert as
   the preferred recipient, **Then** the workflow centers that expert while still
   allowing optional outreach to additional selected experts.
4. **Given** a selected expert has no available slots, **When** the requester creates
   outreach, **Then** the system allows the requester to send the message without
   choosing a meeting time and makes clear that time coordination must happen later.

---

### User Story 3 - Track OHBM 2026 Bordeaux Scheduling Demand (Priority: P3)

As an expert or organizer, I want each OHBM 2026 Bordeaux availability slot to show how many
people have requested that time so that individual or group demonstrations can be
managed without closing popular slots.

**Why this priority**: The event uses a shared demonstration-style calendar rather
than one-to-one exclusive bookings, so the system needs to measure slot demand rather
than block a slot after the first request.

**Independent Test**: Send multiple outreach requests for the same expert and slots
and confirm that attendee counts increase while those slots remain selectable.

**Acceptance Scenarios**:

1. **Given** an expert has a visible availability slot, **When** one requester sends
   outreach for that slot, **Then** the slot's attendee count increases by one.
2. **Given** a requester selects multiple slots for the same expert, **When** the
   outreach is sent, **Then** each selected slot's attendee count increases and each
   chosen time is included in the outreach message.
3. **Given** an expert already has one or more requests for a slot, **When** another
   requester selects the same slot, **Then** the slot remains selectable and the
   attendee count increases again.

### Edge Cases

- A person submits a profile using an email address or ORCID ID that already exists in
  the system.
- An expert omits an ORCID ID but provides the rest of the required profile details.
- An ORCID record exists but fewer than 25 recent first-author or last-author
  publications are available.
- A harvested publication has no abstract or the abstract cannot be reconstructed.
- A verification link expires before the expert confirms their email address.
- An expert does not supply any explicit availability preferences during profile
  submission.
- An expert uses the email lookup flow for an address that is not registered.
- An expert uses a valid edit link to replace their ORCID ID after the original
  publication enrichment has already completed.
- An expert attempts to remove every expertise entry during an edit.
- An expert attempts to delete their profile but enters a different email address in
  the irreversible-confirmation step.
- An expert provides only some optional public profile links and leaves the rest
  blank.
- Several of the highest scoring search documents belong to one expert while fewer
  than 5 distinct experts satisfy the similarity threshold.
- A requester selects a slot that becomes unavailable before the outreach request is
  finalized.
- A requester selects multiple slots for the same expert in one outreach.
- Multiple requesters choose the same expert and the same time slot.
- A selected expert has no available slots but should still be contactable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow an expert to submit a profile through an
  unauthenticated POST request without creating an account.
- **FR-002**: The system MUST require an expert submission to include a name, email
  address, and one or more expertise entries, plus optional ORCID ID, website URL,
  X handle, LinkedIn identifier, Bluesky identifier, and GitHub handle fields.
- **FR-003**: The system MUST validate the submitted email address format and require
  email verification before the profile becomes discoverable.
- **FR-004**: The system MUST validate the ORCID ID format when provided and confirm
  that the ORCID record exists before the ORCID data is used for enrichment.
- **FR-005**: The system MUST treat repeated expert submissions using the same email
  address or ORCID ID as an update path or duplicate-resolution flow instead of
  creating an uncontrolled duplicate discoverable profile.
- **FR-006**: The system MUST store each manually entered expertise entry as a
  separate searchable text unit associated with the same expert.
- **FR-007**: When an ORCID ID is provided and validated, the system MUST retrieve up
  to 25 of the expert's most recent publications, prioritizing works where the expert
  is listed as first or last author and then filling the remainder from other
  authorship positions if needed.
- **FR-008**: For each selected publication, the system MUST attempt to obtain an
  abstract and, when an abstract is available, store it as a separate searchable text
  unit associated with the same expert.
- **FR-009**: The system MUST preserve publication metadata and enrichment status even
  when an abstract is unavailable.
- **FR-010**: The system MUST generate canonical availability slots for each expert at
  15-minute increments in the `Europe/Paris` timezone for June 14, 2026 through
  June 18, 2026, with slot start times from 08:00 through 16:45 so meetings end by
  17:00 local time.
- **FR-011**: The system MUST allow an expert to mark any of those canonical slots as
  unavailable during profile submission or later through an email-based expert-edit
  flow.
- **FR-012**: If an expert does not explicitly provide availability preferences, the
  system MUST mark all canonical slots in that date range as available by default.
- **FR-013**: The system MUST provide a platform flow where an expert enters their
  exact email address to request an expert-edit link.
- **FR-014**: When the email-lookup flow finds a matching expert profile, the system
  MUST send a one-time expert-edit link to that email address instead of requiring
  login credentials.
- **FR-015**: The system MUST allow an expert using a valid one-time expert-edit link
  to update editable profile fields including expertise entries, optional ORCID ID,
  optional public profile links, and OHBM 2026 Bordeaux availability without creating an
  account.
- **FR-016**: The system MUST allow an expert using a valid one-time expert-edit link
  to permanently delete their profile and associated discoverable data only after the
  expert re-enters the exact email address on file as an irreversible confirmation.
- **FR-017**: If an expert changes their ORCID ID through the expert-edit flow, the
  system MUST re-run ORCID validation and refresh ORCID-derived publication metadata
  plus publication-based searchable documents before newly derived content becomes
  active.
- **FR-018**: The system MUST enforce that a discoverable expert profile retains at
  least one expertise entry after any expert-edit submission that does not delete the
  profile.
- **FR-019**: The system MUST store submitted expert profiles in a way that makes
  active profiles discoverable for future matching.
- **FR-020**: The system MUST make optional website and public social account fields
  available to requesters wherever expert details are shown.
- **FR-021**: The system MUST rank experts by comparing a requester's question to all
  searchable text units associated with that expert and aggregating those document
  scores into one expert-level result.
- **FR-022**: The system MUST apply a cosine similarity threshold to expert matching,
  with an initial default value of `0.5`, and make that threshold configurable for
  operators.
- **FR-023**: The system MUST ensure that each expert appears at most once in a query
  result set even if multiple expertise entries or publication abstracts for that
  expert rank highly.
- **FR-024**: The system MUST return no more than 5 distinct experts for a requester
  query and MAY return fewer when fewer than 5 experts satisfy the similarity
  threshold.
- **FR-025**: The system MUST allow experts to be represented by enough profile and
  publication detail for requesters to understand why they were returned as a match.
- **FR-026**: The system MUST allow a requester to submit a free text question about
  the expertise they need without creating an account.
- **FR-027**: The system MUST show each returned expert with identifying details,
  expertise context, optional public profile links, and currently available
  OHBM 2026 Bordeaux slots sufficient for a requester to decide whether to contact them.
- **FR-028**: The system MUST allow a requester to select one preferred expert and up
  to 4 additional experts from the ranked results, for a maximum of 5 selected
  experts per outreach workflow.
- **FR-029**: If a selected expert has no available slots, the system MUST still allow
  the requester to create outreach without requesting a meeting time.
- **FR-030**: The system MUST generate an outreach message for each selected expert
  that includes the requester's question and, when provided, the full list of chosen
  meeting times.
- **FR-031**: The system MUST require each outreach workflow to designate exactly one
  selected expert as the primary expert so the interface and email drafting flow
  remain centered on one preferred recipient even when additional experts are also
  contacted.
- **FR-032**: For each outreach message sent, the system MUST increment the attendee
  count for every selected slot for that expert.
- **FR-033**: A slot with existing attendee requests MUST remain available for future
  outreach unless the expert explicitly marks it unavailable.
- **FR-034**: The system MUST show the current attendee count for each available slot
  wherever the slot is presented for requester selection.
- **FR-035**: The system MUST track outreach status for each selected expert so the
  requester can distinguish pending, sent, failed, declined, and completed contact
  attempts.
- **FR-036**: The system MUST allow the requester to revise their question or stop the
  workflow when no suitable expert match is found.

### Non-Functional Requirements

- **NFR-001**: A newly verified expert profile with no more than 25 harvested
  publications MUST become discoverable to requesters within 10 minutes of successful
  email verification.
- **NFR-002**: For a catalog of up to 1,000 active expert profiles and their
  associated searchable text units, 95% of requester searches MUST present ranked
  matches within 10 seconds.
- **NFR-003**: Availability slot reads, including attendee counts, MUST reflect the
  latest persisted slot state within 5 seconds of an outreach request being recorded.
- **NFR-004**: The application MUST make it clear to a requester or expert when
  profile submission, verification, ORCID enrichment, expert matching, slot
  selection, message delivery, expert profile updates, profile deletion, or
  email-lookup recovery have failed.
- **NFR-005**: Production data stored in PostgreSQL MUST be protected by automated
  backups and a documented restore process.
- **NFR-006**: A successfully deleted expert profile MUST stop appearing in match
  results and expert-detail views within 1 minute of confirmed deletion.

### Benchmark Budgets

- **BB-001**: Before release, representative evaluation runs MUST measure search
  quality and search speed against expert pools of 10, 100, and 1,000 active expert
  profiles, including experts with both manually entered expertise and harvested
  publication abstracts.
- **BB-002**: Benchmark results MUST show that at least 80% of representative
  requester questions return a human-judged relevant expert within the top 5 results.
- **BB-003**: Benchmark runs MUST capture the time from question submission to ranked
  result display and the time required to fetch availability plus attendee counts for
  selected experts.

### Deployment Expectations

- **DE-001**: Stakeholders MUST be able to validate expert profile submission, email
  verification, email-based expert-edit recovery, profile deletion, ORCID
  enrichment, profile editing for June 14, 2026 through June 18, 2026, expert
  discovery, outreach generation, and slot attendee counting in a pre-release
  environment before launch.
- **DE-002**: Any release that changes expert matching, outreach delivery, or
  OHBM 2026 Bordeaux scheduling behavior MUST document how the change will be introduced
  without leaving users in an incomplete workflow.
- **DE-003**: The live service MUST provide visible service status indicators for
  expert profile intake, verification, question matching, outreach delivery, email
  recovery, and slot count updates.
- **DE-004**: The initial production deployment MUST target a simpler AWS layout for
  10-3000 users: the Vite frontend and Python backend run on a single EC2 host under
  Docker Compose, while PostgreSQL is provided as a separately managed service.
- **DE-005**: The production PostgreSQL deployment MUST have automated backups,
  off-instance backup storage, and a restore-validation procedure.
- **DE-006**: Local development and integration environments MAY run PostgreSQL as a
  Docker Compose service backed by a named Docker volume, but that local persistence
  pattern MUST NOT be treated as the production AWS database strategy.
- **DE-007**: Development, test, and production environments SHOULD share the same
  backend image shape, service names, environment-variable contract, and `/api`
  routing pattern wherever practical, while still allowing development-only tooling
  such as hot reloading.
- **DE-008**: The production frontend MUST be served from built static assets through
  the production ingress layer, while local development MAY use a dev server for
  faster iteration if the external request paths remain compatible with production.

### Key Entities *(include if feature involves data)*

- **Expert Profile**: A discoverable record containing a person's identity, contact
  information, optional ORCID ID, optional public profile links, verification state,
  enrichment state, and current discoverability status.
- **Expertise Entry**: One manually entered expertise text item belonging to an expert
  and stored as its own searchable unit.
- **Publication Record**: A publication linked to an expert through ORCID enrichment,
  including authorship priority, publication metadata, and abstract retrieval status.
- **Search Document**: A single searchable text unit derived from either a manual
  expertise entry or a harvested publication abstract and associated with one expert.
- **Expert Availability Slot**: One canonical 15-minute OHBM 2026 Bordeaux time slot in
  Bordeaux time for a specific expert, including availability state and attendee
  count.
- **Expert Edit Session**: A one-time email-based recovery session that lets an
  expert update editable profile fields, including ORCID ID, expertise entries,
  public profile links, and availability, or permanently delete the profile after
  email reconfirmation, without having an account.
- **Expert Query**: A requester's free text description of the question or expertise
  need they want help with.
- **Match Result**: A ranked pairing between an expert query and a candidate expert
  profile, including the information needed to explain which expertise entry or
  publication abstract drove the match, while ensuring only one result row per
  distinct expert.
- **Outreach Request**: The requester's selected expert list, original question,
  chosen primary expert, chosen optional slots for each expert, message content, and
  send status for each chosen expert.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In pilot usage, at least 90% of invited experts can submit a profile
  with one or more expertise entries in under 4 minutes without assistance.
- **SC-002**: In representative evaluation, at least 80% of requester questions
  return a judged relevant expert within the top 5 results.
- **SC-003**: At least 90% of requesters can move from entering a question to sending
  outreach, with or without selected meeting slots, in under 5 minutes.
- **SC-004**: At least 95% of outreach messages sent through the application include
  the original question, the intended recipient, and all selected meeting times when
  times were chosen.
- **SC-005**: At least 90% of verified expert submissions with valid ORCID IDs finish
  publication enrichment and become searchable within 10 minutes.

## Assumptions

- Experts who submit profiles consent to being discovered and contacted for
  conversations related to the expertise they describe.
- Experts and requesters do not create accounts; identity confirmation relies on
  email verification and signed action links rather than logins.
- Bordeaux scheduling is represented by the `Europe/Paris` timezone and the event
  calendar is limited to June 14, 2026 through June 18, 2026 for this release.
- If an expert does not explicitly change their availability, all canonical event
  slots are treated as available by default.
- Experts recover their profile editor by entering their exact email address and
  using the emailed one-time edit link to update expertise, ORCID, public profile
  links, availability, or permanently delete the profile after re-entering their
  email as confirmation.
- Requesters provide enough identifying contact information for experts to reply and
  continue the outreach workflow.
- ORCID enrichment uses only public ORCID records and public publication metadata or
  abstract sources.
- Matching returns at most 5 distinct experts at or above the configured cosine
  similarity threshold, which starts at `0.5`.
- A requester designates one preferred expert in each outreach workflow, even when
  contacting additional experts.
- Optional website and social profile identifiers are self-reported by experts.
- Initial production deployment favors operational simplicity over Kubernetes and
  uses a single EC2 host for the application containers plus a separately managed
  PostgreSQL service.
- Local Docker Compose may include PostgreSQL with named-volume persistence, but AWS
  production database durability relies on managed PostgreSQL rather than a
  container-managed data directory.
- Environment parity matters more than identical process managers: local and
  production should preserve the same public URLs, backend API paths, service names,
  and configuration keys even if the frontend uses a dev server locally and static
  assets plus a reverse proxy in production.
- Formal admin moderation and complex profile approval workflows are out of scope for
  the initial release.

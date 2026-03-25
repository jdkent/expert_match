# Phase 0 Research: Expert Matching and Outreach

## Deployment Baseline

**Decision**: Deploy the application to AWS with Docker Compose on a single EC2 host
for the frontend and backend. For local development, run PostgreSQL as a Docker
Compose service backed by a named Docker volume. For AWS production, use managed
PostgreSQL as a separate service instead of storing database state in the EC2-hosted
Compose stack.

**Rationale**: The target load is only 10-3,000 users, and the clarified deployment
goal explicitly favors a simpler operational model. A single EC2 host keeps compute
operations understandable for v1. A local Compose database makes developer setup and
integration testing simple, while separately managed PostgreSQL in AWS removes the
highest-risk stateful component from the application host.

**Alternatives considered**:

- Additional self-managed orchestration on EC2: rejected because it adds operational
  complexity the expected traffic envelope does not justify.
- Managed container orchestration: rejected for v1 because a single EC2 host plus
  Docker Compose is simpler to operate and matches the chosen architecture.
- Running production PostgreSQL inside the EC2 Compose stack with a Docker volume:
  rejected because persistence, backup, recovery, patching, and failover remain
  self-managed even if the container filesystem is backed by durable host storage.

## Local Development Database Workflow

**Decision**: Add a local `postgres` Compose service for development and integration
testing, backed by an explicit named volume such as `postgres_data`, with the backend
connecting to it through an internal service hostname.

**Rationale**: This matches the normal Docker development workflow, keeps local setup
repeatable, and preserves data between `docker compose down` and `docker compose up`
cycles until the operator intentionally removes the volume.

**Alternatives considered**:

- Local managed PostgreSQL or cloud-only development database: rejected because it
  adds setup friction and makes offline or isolated development harder.
- Bind-mounting the PostgreSQL data directory into the repository: rejected because
  named Docker volumes are a cleaner default for database persistence and avoid
  repository permission and filesystem-noise issues.

## AWS Service Selection

**Decision**: Use EC2, Route 53, ACM, Amazon SES, and managed PostgreSQL in v1. Do
not add ElastiCache, SQS, or dedicated calendar services initially.

**Rationale**: This feature needs persistent storage, API compute, static asset
serving, outbound email, OHBM 2026 Bordeaux availability tracking, and durable backups.
Managed PostgreSQL lowers operational risk for the only persistent stateful runtime.
SES also supports the email-based expert-edit recovery flow without introducing a
separate identity system.

**Alternatives considered**:

- Amazon ElastiCache: rejected for v1 because the expert corpus is small enough that
  in-process caching and PostgreSQL are simpler and cheaper.
- External calendar platforms: rejected because the product only needs a fixed
  OHBM 2026 Bordeaux slot calendar and optional-timeslot outreach.

## AWS PostgreSQL Operations

**Decision**: In AWS, run PostgreSQL on Amazon RDS for PostgreSQL with automated
backups enabled, point-in-time recovery retained, and non-production restore
validation. For this v1 scale, default to Single-AZ when minimizing cost is the
primary concern, and reserve Multi-AZ for environments where the added high
availability requirement justifies the extra cost.

**Rationale**: This keeps the simple EC2 + Docker Compose application deployment
while shifting database durability, backup scheduling, storage snapshots, and engine
maintenance to AWS-managed infrastructure. Single-AZ keeps costs lower for the
10-3,000 user target. Multi-AZ is valuable, but it should be an explicit
availability decision rather than the automatic default for a cost-sensitive v1.

**Alternatives considered**:

- PostgreSQL in Docker on EC2 with a named volume: rejected for production because
  the Docker volume still lives on self-managed EC2 or EBS storage and leaves
  failover, patching, snapshots, and recovery operations on the application team.
- Amazon Aurora PostgreSQL-Compatible Edition: rejected for v1 because the workload
  and cost target do not require its additional clustering and scaling features yet.

## Ingress and Traffic Routing

**Decision**: The current implementation directly publishes the frontend container on
port `80` and the backend container on port `8000`, but the recommended production
shape is to add a single Nginx reverse-proxy container as the only public entrypoint
on the EC2 host. Nginx should terminate HTTP or HTTPS on `80/443`, serve the built
frontend assets, and proxy `/api` requests to the backend container over the Docker
network. If the team later wants AWS-managed TLS and routing, an Application Load
Balancer with ACM can sit in front of that single entrypoint.

**Rationale**: Right now the production Compose file exposes both application
containers directly, which is acceptable for local development but is not the cleanest
production ingress model. A single reverse proxy removes the public backend port,
centralizes headers and request logging, and gives the application one stable public
origin. Nginx fits the current single-host, cost-sensitive deployment better than
adding an ALB immediately, while still leaving the door open for an ALB later.

**Alternatives considered**:

- Keep direct port exposure for both frontend and backend: rejected because it leaves
  the backend publicly reachable and does not provide a unified ingress layer.
- Use an Application Load Balancer immediately: rejected for v1 because it adds cost
  and infrastructure complexity before the application proves it needs managed load
  balancing and TLS termination.
- Keep the frontend on the Vite dev server in production: rejected because it is a
  development server rather than the intended long-running production web serving
  layer.

## Environment Parity and Build Strategy

**Decision**: Keep one logical service graph across environments: `frontend`,
`backend`, and `postgres` locally, with the same `/api` routing contract and the
same application environment variables. Use the same backend image shape across
development, test, and production. For the frontend, allow two runtime targets from
the same source tree: a development target with Vite for local iteration and a
production target that builds static assets served through Nginx. Prefer a shared
base Compose file plus environment-specific overrides rather than three unrelated
deployment definitions.

**Rationale**: The highest-value compatibility is not making every process identical;
it is preserving the same boundaries, routes, and configuration contracts so behavior
transfers cleanly from laptop to EC2. A Vite dev server is useful locally, but it
should not force production to look like development. Shared Compose structure with
overrides keeps deployment simple while minimizing drift.

**Alternatives considered**:

- Make dev identical to prod by forcing Nginx and prebuilt frontend assets in every
  local workflow: rejected because it slows iteration and makes ordinary frontend
  development unnecessarily heavy.
- Maintain completely separate dev, test, and prod stack definitions: rejected
  because configuration drift becomes more likely and deployment behavior becomes
  harder to reason about.
- Run Vite in production for strict parity: rejected because the dev server is not
  the intended production-serving layer.

## Public Expert Submission and Recovery

**Decision**: Expert profile creation remains a public POST flow with no accounts, no
sign-up, and no login. Later profile edits are recovered by exact-email lookup that
sends a one-time edit link to the expert's email address and unlocks editing of
availability, ORCID ID, expertise entries, optional public profile links, and
irreversible profile deletion after email re-confirmation.

**Rationale**: This keeps expert onboarding low-friction while still preventing open
public modification of an expert's profile. The platform can expose an email search
box without leaking profile ownership because the real edit privilege is granted
through the emailed one-time link, and a single recovery flow avoids introducing
separate account-management UX just to maintain expertise details. Requiring the
expert to type their email again before deletion reduces accidental removals without
adding a full authentication system.

**Alternatives considered**:

- Full expert accounts: rejected because they add user-management overhead that the
  product explicitly does not need.
- Anonymous direct profile edit by email lookup alone: rejected because anyone who
  knows an email address could tamper with profile data.

## Public Expert Metadata

**Decision**: Allow experts to optionally publish a website URL plus self-reported X,
LinkedIn, Bluesky, and GitHub identifiers as part of profile creation and profile
editing.

**Rationale**: Requesters need lightweight external context to judge whether an expert
is relevant before sending outreach. Optional handles are cheap to store, easy to
present, and do not require separate social-login integrations.

**Alternatives considered**:

- No external links: rejected because it removes useful context for evaluating expert
  relevance.
- Full social-profile enrichment: rejected because it adds unnecessary integration
  complexity and rate-limit risk for v1.

## ORCID Validation and Publication Harvesting

**Decision**: Validate ORCID IDs against the public ORCID record API, then use the
ORCID ID to resolve the author's works through OpenAlex for publication selection and
abstract harvesting. When an expert changes their ORCID ID in the expert-edit flow,
re-run validation and replace the active ORCID-derived publication corpus for that
expert.

**Rationale**: ORCID is the authoritative identifier to confirm that the submitted ID
exists. OpenAlex exposes work lists by ORCID, authorship position, publication dates,
and abstract data in one consistent API. Recomputing ORCID-derived publications after
an edit keeps the expert's searchable corpus aligned with their latest declared
scholarly identity.

**Alternatives considered**:

- ORCID alone for publication enrichment: rejected because ORCID work summaries are
  not rich enough for author-position prioritization and abstract retrieval.

## OHBM 2026 Bordeaux Availability Model

**Decision**: Represent expert scheduling as canonical 15-minute slots in the
`Europe/Paris` timezone for June 14, 2026 through June 18, 2026, with slot starts
from 08:00 through 16:45 local time. If an expert provides no explicit preferences,
all slots default to available. If an expert later has no available slots, requesters
may still send outreach without selecting a time.

**Rationale**: The request describes a bounded event-style availability window rather
than open-ended calendar scheduling. Canonical slots make the frontend simpler, keep
the backend deterministic, and avoid time-range overlap logic. Allowing outreach with
no timeslots preserves contactability even when an expert opts out of the fixed slot
calendar.

**Alternatives considered**:

- Free-form availability ranges: rejected because overlap handling and validation are
  more complex than the event requires.
- Mandatory slot selection for every outreach: rejected because the user explicitly
  wants requesters to still be able to contact experts who have no availability.

## Outreach and Slot Counting

**Decision**: Send expert outreach emails through Amazon SES and allow the requester
to choose one primary expert and optionally additional experts, with multiple
available OHBM 2026 Bordeaux slots per selected expert or no slots at all when none are
available. Each sent outreach increments the attendee count of every chosen slot, but
the slots remain selectable for future requests.

**Rationale**: This matches the requested group-demonstration behavior better than a
reservation model. A slot-count approach surfaces demand without locking popular
times, and multiple selected slots provide flexibility when the requester wants to
offer several options in one message. Requiring one primary expert keeps the UI
focused on the most likely recipient while still supporting fallback outreach.

**Alternatives considered**:

- One-to-one reservation locking: rejected because the user explicitly wants multiple
  people to be able to choose the same slot.
- Single-slot-only outreach: rejected because the user explicitly wants multiple
  selectable timeslots in one outreach.

## Search Document Storage and Ranking

**Decision**: Store each manual expertise entry and each harvested publication
abstract as a separate `ExpertSearchDocument` linked to one `ExpertProfile`, then
rank experts by aggregating document-level cosine similarity scores, applying a
configurable expert-level cosine threshold that starts at `0.5`, deduplicating by
expert, and returning at most 5 distinct experts per query.

**Rationale**: This preserves distinct expertise signals and avoids flattening a
person's profile into one large text blob. The threshold prevents weak matches from
appearing, and expert-level deduplication avoids one prolific expert occupying
multiple spots in a short result list.

**Alternatives considered**:

- Returning top documents instead of top experts: rejected because requesters need to
  choose people, not text fragments.
- No similarity threshold: rejected because low-signal matches would still surface in
  sparse corpora.

## Backup Strategy

**Decision**: Protect PostgreSQL with managed automated backups, point-in-time
recovery where available, and scheduled restore verification into a non-production
environment.

**Rationale**: Managed PostgreSQL removes the need to operate a backup sidecar or WAL
archive service directly, but restore validation is still required to ensure backups
are usable.

**Alternatives considered**:

- Relying only on Docker volumes or EC2 disk persistence for production durability:
  rejected because durable host storage is not a substitute for managed backups,
  restore workflows, and database-aware operational controls.

# Implementation Plan: Expert Matching and Outreach

**Branch**: `001-expert-matching-app` | **Date**: 2026-03-24 | **Spec**: [/home/jdkent/projects/match_experts/expert_match/specs/001-expert-matching-app/spec.md](/home/jdkent/projects/match_experts/expert_match/specs/001-expert-matching-app/spec.md)
**Input**: Feature specification from `/specs/001-expert-matching-app/spec.md`

## Summary

Build a three-tier expert matching application with a Vite-based React frontend, a
FastAPI backend, and PostgreSQL as the system of record. Expert profile submission is
unauthenticated: a public POST creates a pending profile, sends an email verification
link, and then triggers ORCID-driven publication enrichment when an ORCID ID is
present. Manual expertise entries and harvested publication abstracts are each stored
as separate searchable documents with SPECTER2 embeddings in PostgreSQL using
`pgvector`. Expert profiles may also include optional public context such as a
website URL and self-reported X, LinkedIn, Bluesky, and GitHub identifiers. Expert
scheduling is modeled as canonical 15-minute slots in the `Europe/Paris` timezone for
June 14, 2026 through June 18, 2026. Experts may later recover a one-time
expert-edit link by entering their exact email address; that link allows them to
update availability, expertise entries, public profile links, and optional ORCID ID,
or permanently delete their profile after re-entering their email as irreversible
confirmation. If the ORCID changes, the backend revalidates it and refreshes
ORCID-derived publications and search documents. If an expert never submits
availability, all slots default to available. Requester questions are embedded at
query time, matched against search documents with cosine similarity, rolled up to
expert-level rankings, filtered by a configurable threshold that starts at `0.5`,
deduplicated by expert, and capped at 5 distinct matches. During outreach creation,
the requester designates one preferred expert and may optionally contact up to 4
additional experts. Each selected expert may receive multiple candidate slots, or no
slots at all if that expert currently has no availability. Each sent outreach
increments the attendee count of every chosen slot while leaving those slots
available for additional group-demand bookings. Local development uses Docker
Compose with a `postgres` service backed by a named Docker volume so database state
persists across normal local shutdowns. Initial AWS deployment uses Docker Compose on
a single EC2 host for the frontend and backend, but keeps PostgreSQL outside that
stack on Amazon RDS for PostgreSQL, with automated backups, point-in-time recovery,
and restore validation handled through the managed database service. Public traffic
should enter through a single Nginx reverse-proxy layer on the EC2 host rather than
through separate published frontend and backend ports. Development, test, and
production should keep the same service boundaries and `/api` routing contract even
when the frontend uses a Vite dev target locally and built static assets behind
Nginx in production.

## Technical Context

**Language/Version**: TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence  
**Primary Dependencies**: Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, Nginx for production reverse proxy and static asset serving, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration, Docker Compose base-plus-override configuration for environment parity  
**Storage**: Local development uses PostgreSQL 16 in Docker Compose with a named volume for persistent developer data; AWS uses Amazon RDS for PostgreSQL 16 with `pgvector` for expert profiles, optional public profile metadata, expertise entries, publication records, searchable document embeddings, canonical availability slots, one-time expert-edit sessions, query records with similarity-threshold metadata, distinct match results, outreach state, outreach-slot links, and slot attendee counts; in-process TTL caching for hot read paths; managed backups plus restore validation; no dedicated cache service in v1  
**Testing**: Vitest, React Testing Library, Playwright, pytest, pytest-asyncio, httpx contract tests, Docker Compose smoke tests, retrieval benchmark scripts for 10, 100, and 1,000-plus embedding corpora, ORCID/OpenAlex integration fixtures, profile-edit and email-recovery tests, profile-deletion confirmation tests, threshold and dedup ranking tests, slot-count concurrency tests, and backup restore drills  
**Target Platform**: Linux containers for local Docker Compose and AWS EC2-hosted Docker Compose workloads, with a local Compose PostgreSQL service in development, Nginx as the production ingress container on EC2, and Amazon RDS for PostgreSQL in AWS  
**Project Type**: Web application with separate frontend, backend, and database tiers  
**Performance Goals**: Verified expert submissions with no more than 25 harvested publications become searchable within 10 minutes of email confirmation; ORCID changes submitted through expert-edit links propagate refreshed publication search documents within 10 minutes; successful profile deletions disappear from discovery within 1 minute; p95 query response under 3 seconds for 100 expert profiles and under 8 seconds for 1,000 expert profiles on CPU-only infrastructure while enforcing the distinct-expert top-5 cap; p95 availability-slot fetch under 1 second for a selected expert; slot attendee counts visible within 5 seconds of outreach creation; database restore point objective under 24 hours and recovery point objective under 1 hour  
**Constraints**: MUST use SPECTER2 embeddings and cosine similarity; MUST keep Vite frontend, Python backend, and PostgreSQL boundaries; MUST allow public expert submission without login or account creation; MUST validate submitted email and provided ORCID IDs; MUST harvest at most 25 recent ORCID-linked publications with first or last author priority; MUST store manual expertise entries and publication abstracts as separate expert-linked embeddings; MUST model expert availability as 15-minute slots in `Europe/Paris` from June 14, 2026 through June 18, 2026 with slot starts from 08:00 through 16:45; MUST default all slots to available when an expert provides no explicit availability; MUST support exact-email recovery of one-time expert-edit links; MUST allow one-time expert-edit submissions to change expertise entries, optional ORCID ID, optional website and social identifiers, and availability without changing the accountless model; MUST permit irreversible profile deletion only after exact-email confirmation inside a valid expert-edit session; MUST revalidate and refresh ORCID-derived data when ORCID changes; MUST keep at least one expertise entry per discoverable expert profile unless the expert deletes the profile; MUST apply an operator-configurable cosine similarity threshold that starts at `0.5`; MUST deduplicate matches so one expert occupies at most one result slot; MUST return and allow selection of at most 5 distinct experts per query workflow, while still allowing fewer when insufficient experts qualify; MUST require one selected expert to be marked as the primary outreach target; MUST allow outreach without timeslots when an expert has no availability; MUST allow multiple selected slots per expert in one outreach; MUST increment attendee counts for each selected slot while keeping slots selectable for group demonstrations; MUST provide Docker Compose local orchestration; MUST support a local Compose PostgreSQL service with named-volume persistence for development and test environments; MUST keep AWS production PostgreSQL outside the EC2 Compose stack and use managed PostgreSQL with automated backups and restore validation; MUST expose production traffic through a single reverse-proxy ingress rather than directly publishing both frontend and backend service ports; MUST maximize parity by keeping the same service names, `/api` routing contract, backend image shape, and environment-variable contract across dev, test, and production unless there is a concrete productivity reason not to; MUST minimize AWS spend for 10-3,000 users by avoiding unnecessary orchestration layers and managed services; MUST favor human-centered flows, explainable ranking output, structured logs, health or readiness checks, and automated database backups; benchmark assumptions target a 2 vCPU / 8 GiB application host and managed PostgreSQL sized for low-write, bursty read traffic  
**Scale/Scope**: 10-3,000 total users, tens to low thousands of active expert profiles, dozens of searchable documents per expert, up to 180 canonical slots per expert during the event window, low write volume, bursty read-heavy search traffic, and moderate contention on popular availability slots

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

### Pre-Design Gate

- PASS: The design keeps a Vite frontend, Python backend, and PostgreSQL database as
  separate tiers with explicit API boundaries.
- PASS: Local orchestration uses `docker-compose.yml`, and AWS deployment is a
  simpler containerized topology on a single EC2 host rather than a heavier
  orchestrator, while keeping production PostgreSQL on a managed service rather than
  inside the application Compose stack, and while routing public traffic through one
  reverse-proxy ingress layer instead of directly exposing every service.
- PASS: Semantic retrieval is fixed to SPECTER2 embeddings with cosine similarity and
  stores vectors in PostgreSQL through `pgvector`, with one vector per expertise
  entry or publication abstract.
- PASS: Benchmark scope covers 10, 100, and 1,000-plus expert profile corpora with
  explicit latency targets, human-judged relevance checks, mixed document sources,
  threshold and dedup behavior, ORCID refresh behavior, deletion visibility timing,
  and slot-fetch plus slot-count update timing.
- PASS: There is no backward-compatibility preservation requirement; implementation
  can prefer the simplest clean-slate design.
- PASS: Tests, structured logs, `/healthz`, `/readyz`, and automated backup checks are
  planned for frontend-backend integration, API correctness, profile editing,
  profile deletion, ranking, slot counting, email recovery, and deployment
  verification.

### Post-Design Re-Check

- PASS: `data-model.md` preserves tier boundaries and defines profile, verification,
  publication, search-document, availability-slot, expert-edit, query, match, and
  outreach entities without adding a fourth runtime tier.
- PASS: `contracts/openapi.yaml` documents the backend interface used by the Vite
  frontend, including unauthenticated expert submission, default or edited OHBM 2026 Bordeaux
  availability, exact-email recovery of expert profile updates, profile deletion,
  optional public profile links, distinct-expert thresholded matching, primary-expert
  outreach, and operational endpoints required for health and readiness.
- PASS: `research.md` justifies using PostgreSQL plus `pgvector`, in-process caching,
  SES, ORCID plus OpenAlex enrichment, fixed OHBM 2026 Bordeaux availability slots,
  attendee-count tracking, one-time expert-edit sessions, expert deletion
  confirmation, configurable thresholded ranking, local Compose PostgreSQL for
  development, managed PostgreSQL backups, and single-host Docker Compose deployment
  on EC2 with a single reverse-proxy ingress plus environment-parity-focused build
  targets as the lowest-complexity design that still meets constitutional deployment
  and performance requirements.
- PASS: `quickstart.md` includes Docker Compose startup, enrichment validation,
  profile-edit validation, deletion validation, thresholded matching validation,
  attendee-count validation, optional-timeslot outreach validation, backup
  validation, local volume-persistence expectations, API smoke tests, and deployment
  checks for the simplified AWS model.

## Project Structure

### Documentation (this feature)

```text
specs/001-expert-matching-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── workers/
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── pages/
│   ├── services/
│   └── styles/
└── tests/
    ├── e2e/
    └── unit/

deploy/
└── aws/
    ├── ec2/
    └── compose/

docker-compose.yml
```

**Structure Decision**: Use a standard web-application split with `frontend/`,
`backend/`, and lightweight deployment assets under `deploy/aws/` so service
boundaries remain explicit in both local development and the simpler AWS rollout.
Retrieval benchmarks live outside the runtime code in `benchmarks/retrieval/` to
keep performance evidence versioned and repeatable. The local `docker-compose.yml`
may include a PostgreSQL service with a named Docker volume for developer
persistence, while deployment artifacts under `deploy/aws/` continue to cover EC2
host setup, Docker Compose production configuration, and managed PostgreSQL
configuration inputs for the simpler AWS hosting model. The preferred rollout shape
is a shared base Compose definition with environment-specific overrides so dev, test,
and production stay structurally aligned.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The current design passes the constitution without exceptions. |

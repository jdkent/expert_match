# expert_match Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-24

## Active Technologies
- Frontend: TypeScript 5.x, Node.js 22 LTS, Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `cachetools`, ORCID Public API integration, OpenAlex API integration
- Data and delivery: PostgreSQL 16 with `pgvector`, local Docker Compose PostgreSQL with a named volume for development, Amazon SES, Docker Compose deployment on AWS EC2 with Amazon RDS for PostgreSQL in production
- Feature context: `001-expert-matching-app`
- Local development uses PostgreSQL 16 in Docker Compose with a named volume for persistent developer data; AWS uses Amazon RDS for PostgreSQL 16 with `pgvector` for expert profiles, optional public profile metadata, expertise entries, publication records, searchable document embeddings, canonical availability slots, one-time expert-edit sessions, query records with similarity-threshold metadata, distinct match results, outreach state, outreach-slot links, and slot attendee counts; in-process TTL caching for hot read paths; managed backups plus restore validation; no dedicated cache service in v1 (001-expert-matching-app)
- TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence + Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, Nginx for production reverse proxy and static asset serving, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration (001-expert-matching-app)
- TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence + Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, Nginx for production reverse proxy and static asset serving, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration, Docker Compose base-plus-override configuration for environment parity (001-expert-matching-app)

## Project Structure

```text
backend/
frontend/
deploy/
benchmarks/retrieval/
specs/001-expert-matching-app/
```

## Commands

- `docker compose up --build`
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
- `docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm backend pytest`
- `docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npm test`
- `docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npx playwright test`
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml config`

## Code Style

- Frontend: keep flows accessible, form-heavy interactions explicit, and server state in TanStack Query rather than ad hoc component state.
- Frontend: keep `/api` calls ingress-relative by default so Vite dev and production Nginx stay behaviorally aligned.
- Backend: keep FastAPI route handlers thin, push ranking and outreach logic into typed services, and preserve clear schema or model separation.
- Backend: treat `POSTGRES_DSN` as the single database contract and keep readiness checks compatible with both local Compose PostgreSQL and Amazon RDS.
- Retrieval: keep SPECTER2 preprocessing and cosine-similarity logic canonical in one pipeline.

## Recent Changes
- 001-expert-matching-app: Added TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence + Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, Nginx for production reverse proxy and static asset serving, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration, Docker Compose base-plus-override configuration for environment parity
- 001-expert-matching-app: Added TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence + Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, Nginx for production reverse proxy and static asset serving, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration
- 001-expert-matching-app: Added TypeScript 5.x with Node.js 22 LTS for the frontend build; Python 3.12 for the backend; PostgreSQL 16 for persistence + Vite, React, React Router, TanStack Query, Tailwind CSS, Radix UI primitives, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, sentence-transformers/Transformers with SPECTER2, `pgvector`, `cachetools`, Amazon SES SDK, ORCID Public API integration, OpenAlex API integration

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

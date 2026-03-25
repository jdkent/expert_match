# Quickstart: Expert Matching and Outreach

## Purpose

Validate the complete feature locally with Docker Compose and verify that the same
runtime assumptions map cleanly to the simplified AWS deployment using Docker Compose
on EC2 plus managed PostgreSQL.

## Production Traffic Shape

Recommended production flow:

- Browser traffic hits one public entrypoint on the EC2 host
- That entrypoint should be an Nginx reverse proxy listening on `80/443`
- Nginx serves the built frontend assets and proxies `/api` to the backend container
- The backend container should not be exposed directly as a second public port in the
  final production shape

## Environment Strategy

Recommended parity model:

- one shared Compose base for service names and internal networking
- a development override that enables Vite hot reload and local PostgreSQL volume persistence
- a test path that reuses the same service graph and env vars but runs automated commands
- a production override that swaps the frontend runtime to built static assets behind Nginx
- the same `/api` paths and backend configuration keys across all environments

## Start the Stack

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
```

Expected result:

- Local development may include a `postgres` Compose service
- PostgreSQL data persists between normal `docker compose down` and `docker compose up`
  cycles through a named Docker volume
- Local data is only removed intentionally, for example with `docker compose down -v`
- AWS production still points the application stack at managed PostgreSQL rather than
  reusing the local database container pattern

## Validate Containerized Test Commands

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm backend pytest
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npm test
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npm run build
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm -v "$PWD:/workspace" --entrypoint python backend /workspace/benchmarks/retrieval/run_benchmarks.py
docker compose -f docker-compose.yml -f docker-compose.dev.yml config
docker compose -f docker-compose.yml -f docker-compose.test.yml config
docker compose -f deploy/aws/compose/docker-compose.prod.yml --env-file deploy/aws/compose/.env.example config
```

Expected result:

- Backend tests pass inside the backend container while the backend points at the local Compose PostgreSQL service
- Frontend unit tests pass inside the frontend container
- Frontend production bundle builds inside the frontend container
- Retrieval benchmark results are written to `benchmarks/retrieval/results/001-expert-matching-app.json`
- Base, dev, test, and production Compose files all render valid config
- The production Compose file expects an external PostgreSQL connection string rather
  than a production `postgres` container

## Validate Expert Submission

```bash
curl -X POST http://localhost:8000/api/v1/experts \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ada Lovelace",
    "email": "ada@example.org",
    "website_url": "https://ada.example.org",
    "github_handle": "ada-lovelace",
    "expertise_entries": [
      "I help with scholarly communication and metadata workflows."
    ]
  }'
```

Expected result:

- Returns `202 Accepted`
- Sends a verification email
- Returns a development verification token that can be used immediately in local flows
- Defaults all June 14-18, 2026 Bordeaux slots to available after verification if no
  explicit availability is supplied

## Validate Expert Edit Recovery by Email

```bash
curl -X POST http://localhost:8000/api/v1/expert-edit-lookup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ada@example.org"
  }'
```

Expected result:

- Sends a one-time expert-edit link to the matching expert email
- Returns a development session token for the local UI flow

Use the recovered session to update profile details and availability:

```bash
curl -X PATCH http://localhost:8000/api/v1/expert-edit-sessions/REPLACE_WITH_TOKEN/profile \
  -H "Content-Type: application/json" \
  -d '{
    "orcid_id": "0000-0002-1825-0097",
    "website_url": "https://ada.example.org",
    "linkedin_identifier": "ada-lovelace",
    "expertise_entries": [
      "I help with scholarly communication and metadata workflows.",
      "I can advise on ORCID adoption and publication data cleanup."
    ],
    "available_slot_ids": [
      "REPLACE_WITH_SLOT_ID_1",
      "REPLACE_WITH_SLOT_ID_2"
    ]
  }'
```

Expected result:

- Updates the expert profile without requiring login
- Replaces the active expertise list with the submitted set
- Revalidates and re-enriches publications if the ORCID ID changed
- Updates the canonical availability slots for the event window

Delete the profile through the same recovered session:

```bash
curl -X DELETE http://localhost:8000/api/v1/expert-edit-sessions/REPLACE_WITH_TOKEN/profile \
  -H "Content-Type: application/json" \
  -d '{
    "email_confirmation": "ada@example.org"
  }'
```

Expected result:

- Deletes the expert profile irreversibly from product workflows
- Removes the expert from future matching and profile views

## Validate Matching and Outreach

```bash
curl -X POST http://localhost:8000/api/v1/match-queries \
  -H "Content-Type: application/json" \
  -d '{
    "requester": {
      "full_name": "Grace Hopper",
      "email": "grace@example.org"
    },
    "query_text": "I need advice on reproducible research workflows."
  }'
```

Expected result:

- Returns up to 5 distinct experts, not 5 documents
- Applies the configured similarity threshold, starting at `0.5`
- May return fewer than 5 experts if not enough profiles qualify

Create outreach centered on one primary expert:

```bash
curl -X POST http://localhost:8000/api/v1/outreach-requests \
  -H "Content-Type: application/json" \
  -d '{
    "match_query_id": "REPLACE_WITH_QUERY_ID",
    "primary_expert_id": "REPLACE_WITH_EXPERT_ID",
    "requester": {
      "full_name": "Grace Hopper",
      "email": "grace@example.org"
    },
    "recipients": [
      {
        "expert_id": "REPLACE_WITH_EXPERT_ID",
        "availability_slot_ids": [
          "REPLACE_WITH_SLOT_ID_1",
          "REPLACE_WITH_SLOT_ID_2"
        ]
      }
    ],
    "message_body": "I would like to discuss reproducible research workflows."
  }'
```

Expected result:

- The workflow is centered on the chosen primary expert
- Includes all selected times in the outreach email
- Increments attendee counts for both selected slots

Create outreach when the expert has no available slots:

```bash
curl -X POST http://localhost:8000/api/v1/outreach-requests \
  -H "Content-Type: application/json" \
  -d '{
    "match_query_id": "REPLACE_WITH_QUERY_ID",
    "primary_expert_id": "REPLACE_WITH_EXPERT_ID_WITHOUT_AVAILABILITY",
    "requester": {
      "full_name": "Grace Hopper",
      "email": "grace@example.org"
    },
    "recipients": [
      {
        "expert_id": "REPLACE_WITH_EXPERT_ID_WITHOUT_AVAILABILITY",
        "availability_slot_ids": []
      }
    ],
    "message_body": "I would still like to connect even if no preset times are available."
  }'
```

Expected result:

- Outreach is still created and sent
- No slot count is incremented
- The message clearly omits fixed requested times

## Validate Backups

```bash
# run a managed PostgreSQL backup/restore validation in the target AWS environment
# according to the provider's backup workflow and restore a copy into non-production
```

Expected result:

- AWS production database backups are handled by the managed PostgreSQL service
- Restore validation targets a non-production restored instance, not a Docker volume

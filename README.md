# Expert Match

Expert Match is a simple accountless workflow for publishing expert profiles,
matching free-text questions to relevant experts, and drafting outreach with optional
OHBM 2026 Bordeaux time proposals.

## Local stack

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm backend pytest
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npm test
docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --no-deps frontend npm run build
docker compose -f docker-compose.yml -f docker-compose.dev.yml config
```

The local development stack keeps three services aligned with production boundaries:
`frontend`, `backend`, and a local `postgres` container backed by the named volume
`postgres_data_pg17`. The frontend runs at `http://localhost:5173`, proxies `/api`,
`/healthz`, and `/readyz` to the backend, and the backend uses `POSTGRES_DSN` to
reach the local Compose database. The Compose Postgres image targets PostgreSQL 17 with
`pgvector`, and the backend uses built-in PostgreSQL full-text search
for lexical ranking so the same approach works on Amazon RDS.

The backend now uses the real OpenAlex API for ORCID-based enrichment. By default it
identifies requests with `APP_OPENALEX_EMAIL=jamesdkent21@gmail.com`, and it also
supports `APP_OPENALEX_API_KEY` if you later want to move beyond the free unauthenticated
request budget.

ORCID validation is also live by default in development and production. The test stack
keeps email delivery, ORCID lookups, and embeddings deterministic so backend tests stay
fast and repeatable while the runtime code stays real.

Development and production now default to
`sentence-transformers/all-mpnet-base-v2` for both stored expert text and
requester question search. The first runtime startup will download that model
into `APP_EMBEDDING_CACHE_DIR`.

## One-shot local bootstrap

To start the dev stack, run migrations, ingest the seeded experts, and leave the app
ready for interactive use:

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend \
  python -m app.scripts.ingest_methods_neuroscientists --api-base-url http://localhost:8000
```

Then open:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`

The first ingestion run can take a while because it may need to download the default embedding model and
fetch live ORCID/OpenAlex data. The seed ingester now uses a longer read timeout by
default so profile creation can wait for that enrichment work to finish.

If you change the embedding model, run the recorded backfills after migrations and
before serving traffic:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend \
  python -m app.scripts.run_backfills
```

## Seeded experts

To load the curated methods-neuroscience seed set into a running local backend and
make those profiles searchable immediately:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend \
  python -m app.scripts.ingest_methods_neuroscientists --api-base-url http://localhost:8000
```

That script posts 20 bundled expert profiles to the running backend, receives the
returned access keys automatically, and stores the experts in the local PostgreSQL
development database so they remain available across backend restarts.

## Architecture

- `frontend/`: Vite + React interface for expert submission, access-key management, matching, and draft generation
- `backend/`: FastAPI service with typed services for expert lifecycle, availability, and matching
- `deploy/aws/`: EC2 + Docker Compose deployment artifacts for the simpler v1 rollout
- `benchmarks/retrieval/`: repeatable retrieval benchmark harness and recorded results

## Production shape

- Use the frontend production image target to serve built static assets from Nginx
- Publish only the frontend ingress on port `80`
- Keep the backend internal to the Compose network
- Point `POSTGRES_DSN` at a PostgreSQL 17 deployment with `pgvector` enabled
- The current frontend is draft-only for requester outreach, so production does not require any SMTP or email transport settings

## AWS instance operations

To stop the current production EC2 instance from the command line:

```bash
aws ec2 stop-instances \
  --profile admin \
  --region us-east-1 \
  --instance-ids i-0d28bb7bab5cce119

aws ec2 wait instance-stopped \
  --profile admin \
  --region us-east-1 \
  --instance-ids i-0d28bb7bab5cce119
```

To start it again:

```bash
aws ec2 start-instances \
  --profile admin \
  --region us-east-1 \
  --instance-ids i-0d28bb7bab5cce119
```

You can also do the same thing from GitHub Actions with two manual workflows:

- `Start AWS Instance`
- `Stop AWS Instance`

They use the existing repo configuration:

- variable: `AWS_REGION`
- variable: `EC2_INSTANCE_ID`
- secret: `AWS_ACCESS_KEY_ID`
- secret: `AWS_SECRET_ACCESS_KEY`

## Let's Encrypt on EC2

The production frontend can run in plain HTTP mode until a real certificate exists,
then switch to HTTPS automatically once Let's Encrypt files are present.

Before requesting the certificate:

1. Point `ohbmatchmaker.org` to the EC2 public IP.
2. Open inbound `443/tcp` on the instance security group.
3. Set `APP_DOMAIN=ohbmatchmaker.org` in `/opt/expert-match/.env` or the GitHub deploy env.

To request the initial certificate on the host:

```bash
chmod +x /opt/expert-match/setup-letsencrypt.sh /opt/expert-match/renew-letsencrypt.sh
/opt/expert-match/setup-letsencrypt.sh ohbmatchmaker.org jamesdkent21@gmail.com
```

To renew manually:

```bash
/opt/expert-match/renew-letsencrypt.sh
```

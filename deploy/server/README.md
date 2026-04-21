# Server deployment

This path deploys the app to a normal Linux server over SSH. It does not use AWS,
ECR, EC2, SSM, or RDS-specific automation.

It reuses the root [docker-compose.yml](../../docker-compose.yml) as the shared base
stack and applies only the production-specific overrides from
[docker-compose.prod.yml](./docker-compose.prod.yml).

## What this deploy path assumes

- The server has Docker Engine and the Docker Compose plugin installed.
- The server keeps a dedicated checkout of this repository.
- The checkout can run `git fetch origin` on the server during deployment.
- If the repository is private, the server checkout has its own GitHub deploy key or
  other non-interactive Git credentials.
- The production stack now includes a `postgres` service backed by a persistent
  Docker volume on the server.
- The remote server already has a shared external Docker network for `nginx-proxy`.

## One-time server setup

1. Clone the repository onto the target host.
2. Copy [`.env.production.example`](./.env.production.example) to `.env.production`
   at the repository root and fill in the real values.
3. Confirm the server user that GitHub Actions SSHes into can run Docker commands.
4. Confirm the external Docker network named by `NGINX_PROXY_NETWORK` already exists.
5. Point your shared `nginx-proxy` stack at this app with `VIRTUAL_HOST`,
   `LETSENCRYPT_HOST`, and `LETSENCRYPT_EMAIL`.

The shared base compose file creates these persistent named volumes on the host:

- `server_postgres_data_pg17`: PostgreSQL data directory
- `server_backend_model_cache`: downloaded embedding model cache

The frontend container joins two networks at runtime:

- the default app network for talking to `backend`
- the external `nginx-proxy` network so the shared reverse proxy can reach it

## GitHub Actions configuration

Add this repository secret:

- `SSH_PRIVATE_KEY`: private key that can SSH to the target server

Add these repository variables:

- `DEPLOY_HOST`: SSH hostname or IP of the target server
- `DEPLOY_USER`: SSH user on the target server
- `DEPLOY_PORT`: optional, defaults to `22`
- `DEPLOY_REPO_ROOT`: absolute path to the repository checkout on the target server
- `DEPLOY_ENV_FILE`: optional, defaults to `.env.production`

## Workflow behavior

The workflow in [`.github/workflows/deploy-server.yml`](../../.github/workflows/deploy-server.yml):

- connects to the server over SSH
- fetches the requested git ref into the existing checkout
- hard-resets that checkout to the deployed ref
- runs [deploy.sh](./deploy.sh), which applies the base plus production override
  compose files, builds the production images on the host, runs migrations,
  optionally runs backfills, and restarts the stack

## Manual deploy

To run the same deployment steps manually on the server:

```bash
cd /path/to/expert_match
/bin/bash ./deploy/server/deploy.sh \
  --repo-root /path/to/expert_match \
  --env-file .env.production
```

Skip backfills when you know the release does not need them:

```bash
cd /path/to/expert_match
/bin/bash ./deploy/server/deploy.sh \
  --repo-root /path/to/expert_match \
  --env-file .env.production \
  --skip-backfills
```

## Restore a production dump on this machine

If you are moving off the external server and want to seed the local Docker
PostgreSQL service from a PostgreSQL custom dump:

```bash
cd /path/to/expert_match
/bin/bash ./deploy/server/restore_dump.sh \
  --repo-root /path/to/expert_match \
  --env-file .env.production \
  --dump /path/to/expert_match-rds-2026-04-21-131803.dump
```

This script:

- starts the local `postgres` service if needed
- drops and recreates `POSTGRES_DB`
- restores the dump into the local database with `pg_restore`

Run the normal deploy first so the app images, schema code, and proxy wiring are in
place, then restore the dump before starting full traffic cutover.

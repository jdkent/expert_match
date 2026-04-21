#!/usr/bin/env bash

set -euo pipefail

repo_root=""
env_file=".env.production"
compose_args=(
  -f docker-compose.yml
  -f deploy/server/docker-compose.prod.yml
)
run_backfills="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      repo_root="$2"
      shift 2
      ;;
    --env-file)
      env_file="$2"
      shift 2
      ;;
    --compose-file)
      compose_args=(-f "$2")
      shift 2
      ;;
    --skip-backfills)
      run_backfills="false"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$repo_root" ]]; then
  echo "--repo-root is required" >&2
  exit 1
fi

cd "$repo_root"

if [[ ! -f "$env_file" ]]; then
  echo "Environment file not found: $env_file" >&2
  exit 1
fi

docker compose "${compose_args[@]}" --env-file "$env_file" config >/dev/null
docker compose "${compose_args[@]}" --env-file "$env_file" build --pull backend frontend
docker compose "${compose_args[@]}" --env-file "$env_file" run --rm backend alembic upgrade head

if [[ "$run_backfills" = "true" ]]; then
  docker compose "${compose_args[@]}" --env-file "$env_file" run --rm backend python -m app.scripts.run_backfills
fi

docker compose "${compose_args[@]}" --env-file "$env_file" up -d --remove-orphans
docker image prune -f >/dev/null 2>&1 || true

#!/usr/bin/env bash

set -euo pipefail

repo_root=""
env_file=".env.production"
dump_path=""
compose_args=(
  -f docker-compose.yml
  -f deploy/server/docker-compose.prod.yml
)
service_name="postgres"

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
    --dump)
      dump_path="$2"
      shift 2
      ;;
    --service)
      service_name="$2"
      shift 2
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

if [[ -z "$dump_path" ]]; then
  echo "--dump is required" >&2
  exit 1
fi

cd "$repo_root"

if [[ ! -f "$env_file" ]]; then
  echo "Environment file not found: $env_file" >&2
  exit 1
fi

if [[ ! -f "$dump_path" ]]; then
  echo "Dump file not found: $dump_path" >&2
  exit 1
fi

docker compose "${compose_args[@]}" --env-file "$env_file" config >/dev/null

postgres_db="$(grep -E '^POSTGRES_DB=' "$env_file" | tail -n 1 | cut -d= -f2-)"
postgres_user="$(grep -E '^POSTGRES_USER=' "$env_file" | tail -n 1 | cut -d= -f2-)"

if [[ -z "$postgres_db" || -z "$postgres_user" ]]; then
  echo "POSTGRES_DB and POSTGRES_USER must be set in $env_file" >&2
  exit 1
fi

docker compose "${compose_args[@]}" --env-file "$env_file" up -d "$service_name"

for attempt in $(seq 1 30); do
  if docker compose "${compose_args[@]}" --env-file "$env_file" exec -T "$service_name" \
    pg_isready -U "$postgres_user" -d postgres >/dev/null 2>&1; then
    break
  fi

  if [[ "$attempt" -eq 30 ]]; then
    echo "Timed out waiting for PostgreSQL to become ready" >&2
    exit 1
  fi

  sleep 2
done

docker compose "${compose_args[@]}" --env-file "$env_file" exec -T "$service_name" \
  psql -U "$postgres_user" -d postgres \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$postgres_db' AND pid <> pg_backend_pid();" \
  >/dev/null

docker compose "${compose_args[@]}" --env-file "$env_file" exec -T "$service_name" \
  dropdb --if-exists -U "$postgres_user" "$postgres_db"

docker compose "${compose_args[@]}" --env-file "$env_file" exec -T "$service_name" \
  createdb -U "$postgres_user" "$postgres_db"

cat "$dump_path" | docker compose "${compose_args[@]}" --env-file "$env_file" exec -T "$service_name" \
  pg_restore --clean --if-exists --no-owner --no-privileges -U "$postgres_user" -d "$postgres_db"


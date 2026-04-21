#!/usr/bin/env bash
set -euxo pipefail

arch="$(uname -m)"
compose_arch="x86_64"
if [[ "$arch" == "aarch64" || "$arch" == "arm64" ]]; then
  compose_arch="aarch64"
fi

dnf install -y ca-certificates curl docker awscli cronie
systemctl enable docker
systemctl start docker
systemctl enable crond
systemctl start crond

mkdir -p /usr/local/libexec/docker/cli-plugins
curl -fL "https://github.com/docker/compose/releases/download/v2.39.4/docker-compose-linux-${compose_arch}" \
  -o /usr/local/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/local/libexec/docker/cli-plugins/docker-compose

mkdir -p /opt/expert-match

if [[ -n "${APP_ENV_SSM_PARAMETER:-}" ]]; then
  aws ssm get-parameter \
    --region "${AWS_REGION:-us-east-1}" \
    --name "$APP_ENV_SSM_PARAMETER" \
    --with-decryption \
    --query Parameter.Value \
    --output text >/opt/expert-match/.env
elif [[ ! -f /opt/expert-match/.env ]]; then
  cat >/opt/expert-match/.env <<'EOF'
BACKEND_IMAGE=ghcr.io/example/expert-match-backend:latest
FRONTEND_IMAGE=ghcr.io/example/expert-match-frontend:latest
APP_PUBLIC_ORIGIN=http://REPLACE_WITH_PUBLIC_HOST
APP_DOMAIN=REPLACE_WITH_DOMAIN
POSTGRES_DSN=postgresql+psycopg://USERNAME:PASSWORD@managed-postgres.example.com:5432/expert_match
EOF
fi

if [[ -n "${COMPOSE_FILE_SSM_PARAMETER:-}" ]]; then
  aws ssm get-parameter \
    --region "${AWS_REGION:-us-east-1}" \
    --name "$COMPOSE_FILE_SSM_PARAMETER" \
    --with-decryption \
    --query Parameter.Value \
    --output text >/opt/expert-match/docker-compose.yml
fi

if [[ -f /opt/expert-match/docker-compose.yml && -f /opt/expert-match/.env && -n "${ECR_REGISTRY:-}" ]]; then
  aws ecr get-login-password --region "${AWS_REGION:-us-east-1}" \
    | docker login --username AWS --password-stdin "$ECR_REGISTRY"
  docker compose -f /opt/expert-match/docker-compose.yml --env-file /opt/expert-match/.env pull
  docker compose -f /opt/expert-match/docker-compose.yml --env-file /opt/expert-match/.env run --rm backend alembic upgrade head
  docker compose -f /opt/expert-match/docker-compose.yml --env-file /opt/expert-match/.env run --rm backend python -m app.scripts.run_backfills
  docker compose -f /opt/expert-match/docker-compose.yml --env-file /opt/expert-match/.env up -d
fi

echo "Bootstrap complete. If docker-compose.yml and runtime env were provided, the stack has been started."

#!/usr/bin/env bash
set -euxo pipefail

dnf install -y ca-certificates curl docker awscli cronie
systemctl enable docker
systemctl start docker
systemctl enable crond
systemctl start crond

mkdir -p /usr/local/libexec/docker/cli-plugins
curl -fL https://github.com/docker/compose/releases/download/v5.1.1/docker-compose-linux-x86_64 \
  -o /usr/local/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/local/libexec/docker/cli-plugins/docker-compose

mkdir -p /opt/expert-match
cat >/opt/expert-match/.env <<'EOF'
BACKEND_IMAGE=ghcr.io/example/expert-match-backend:latest
FRONTEND_IMAGE=ghcr.io/example/expert-match-frontend:latest
APP_PUBLIC_ORIGIN=http://REPLACE_WITH_PUBLIC_HOST
APP_DOMAIN=REPLACE_WITH_DOMAIN
POSTGRES_DSN=postgresql+psycopg://USERNAME:PASSWORD@managed-postgres.example.com:5432/expert_match
EOF

echo "Copy deploy/aws/compose/docker-compose.prod.yml and deploy/aws/ec2/*.sh to /opt/expert-match/, log into ECR, run alembic upgrade head, then docker compose up -d"

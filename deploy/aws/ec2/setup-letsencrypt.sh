#!/usr/bin/env bash
set -euxo pipefail

DOMAIN="${1:?usage: setup-letsencrypt.sh <domain> <email>}"
EMAIL="${2:?usage: setup-letsencrypt.sh <domain> <email>}"
BASE_DIR="${BASE_DIR:-/opt/expert-match}"
LE_DIR="${LE_DIR:-$BASE_DIR/letsencrypt}"
ACME_DIR="${ACME_DIR:-$BASE_DIR/acme-challenge}"

mkdir -p "$LE_DIR" "$ACME_DIR"

docker run --rm \
  -v "$LE_DIR:/etc/letsencrypt" \
  -v "$ACME_DIR:/var/www/certbot" \
  certbot/certbot:latest certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --domain "$DOMAIN"

docker compose -f "$BASE_DIR/docker-compose.yml" --env-file "$BASE_DIR/.env" restart frontend

#!/bin/sh
set -eu

APP_DOMAIN="${APP_DOMAIN:-}"
SERVER_NAME="${APP_DOMAIN:-_}"

if [ -n "$APP_DOMAIN" ] && [ -f "/etc/letsencrypt/live/$APP_DOMAIN/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/$APP_DOMAIN/privkey.pem" ]; then
  export APP_DOMAIN SERVER_NAME
  envsubst '${APP_DOMAIN} ${SERVER_NAME}' \
    < /etc/nginx/templates/default.https.conf.template \
    > /etc/nginx/conf.d/default.conf
else
  export SERVER_NAME
  envsubst '${SERVER_NAME}' \
    < /etc/nginx/templates/default.http.conf.template \
    > /etc/nginx/conf.d/default.conf
fi

exec nginx -g 'daemon off;'

FROM node:22-alpine AS deps

WORKDIR /app

COPY frontend/package.json /app/package.json
RUN npm install

FROM deps AS development

COPY frontend /app

EXPOSE 5173

CMD ["npm", "run", "dev"]

FROM deps AS build

ARG VITE_API_BASE=
ENV VITE_API_BASE=${VITE_API_BASE}

COPY frontend /app

RUN npm run build

FROM nginx:1.27-alpine AS production

RUN apk add --no-cache gettext
COPY deploy/aws/compose/nginx.http.conf.template /etc/nginx/templates/default.http.conf.template
COPY deploy/aws/compose/nginx.https.conf.template /etc/nginx/templates/default.https.conf.template
COPY deploy/aws/compose/frontend-entrypoint.sh /usr/local/bin/frontend-entrypoint.sh
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

CMD ["sh", "/usr/local/bin/frontend-entrypoint.sh"]

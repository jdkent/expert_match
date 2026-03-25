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

COPY deploy/aws/compose/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./

ARG VITE_AUTH_URL=http://localhost:8000
ARG VITE_DISCUSSION_URL=http://localhost:8001
ARG VITE_REALTIME_URL=http://localhost:8002
ARG VITE_NOTIFICATION_URL=http://localhost:8003
ARG VITE_WS_BASE=ws://localhost:8002

ENV VITE_AUTH_URL=${VITE_AUTH_URL} \
    VITE_DISCUSSION_URL=${VITE_DISCUSSION_URL} \
    VITE_REALTIME_URL=${VITE_REALTIME_URL} \
    VITE_NOTIFICATION_URL=${VITE_NOTIFICATION_URL} \
    VITE_WS_BASE=${VITE_WS_BASE}

RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

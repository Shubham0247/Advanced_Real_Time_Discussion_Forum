# Advanced Realtime Discussion Forum

A production-oriented full-stack discussion platform built with **FastAPI microservices**, **PostgreSQL**, **Redis**, and **WebSockets**.
It demonstrates clean architecture, domain separation, realtime collaboration, and scalable backend patterns.

## Project Overview

This project implements a realtime forum where users can:

- register and authenticate with JWT
- create and manage discussion threads
- post nested comments/replies
- like/unlike threads and comments
- receive live UI updates via WebSockets
- receive event-driven notifications

The backend follows a layered architecture:

`routers -> services -> repositories -> models`

This separation keeps business logic testable, APIs clean, and persistence concerns isolated.

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Redis (Pub/Sub)
- JWT Authentication
- WebSockets (realtime channels)

### Frontend

- React
- Vite
- React Query
- Axios

### DevOps / Tooling

- Docker
- Docker Compose
- Nginx (frontend container runtime)
- Pytest

## Features

- JWT-based user registration/login and role-aware authorization
- Thread CRUD with optional image upload
- Nested comment/reply system (self-referencing comment tree)
- Like/unlike for threads and comments
- Realtime event propagation to thread rooms and global feed
- Notification pipeline (mentions, replies, likes, thread comments)
- Moderation/reporting endpoints
- OpenAPI export for all services
- Clean layered microservice design for maintainability

## Folder Structure

```text
Advanced_Real_Time_Discussion_Forum/
|-- backend/
|   |-- services/
|   |   |-- auth_service/app/{api,core,models,repositories,schemas,services}
|   |   |-- discussion_service/app/{api,core,models,repositories,schemas,services}
|   |   |-- notification_service/app/{api,core,models,repositories,schemas,services}
|   |   `-- realtime_service/app/{core,websocket}
|   |-- shared/{database,logging}
|   |-- openapi/
|   |-- docs/
|   `-- scripts/
|-- frontend/{src,public}
|-- docker/{backend.Dockerfile,frontend.Dockerfile,nginx/}
|-- docker-compose.yml
|-- .env.example
|-- .env.docker.example
`-- requirements.txt
```

## Setup Instructions

### 1) Run With Docker (Recommended)

#### Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)

#### Steps

```bash
# from project root
cp .env.docker.example .env.docker   # PowerShell: Copy-Item .env.docker.example .env.docker
```

Update `DOCKER_SECRET_KEY` in `.env.docker`.

```bash
docker compose --env-file .env.docker up --build -d
```

#### Access

- Frontend: `http://localhost:3000`
- Auth Service: `http://localhost:8000`
- Discussion Service: `http://localhost:8001`
- Realtime Service: `http://localhost:8002`
- Notification Service: `http://localhost:8003`

#### Stop

```bash
docker compose --env-file .env.docker down
```

Remove volumes too:

```bash
docker compose --env-file .env.docker down -v
```

### 2) Manual Local Setup

#### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL
- Redis

#### Backend

```bash
# from project root
cp .env.example .env   # PowerShell: Copy-Item .env.example .env
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Start backend services in separate terminals:

```bash
uvicorn backend.services.auth_service.app.main:app --host 0.0.0.0 --port 8000
uvicorn backend.services.discussion_service.app.main:app --host 0.0.0.0 --port 8001
uvicorn backend.services.realtime_service.app.main:app --host 0.0.0.0 --port 8002
uvicorn backend.services.notification_service.app.main:app --host 0.0.0.0 --port 8003
```

#### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## API Documentation

Each FastAPI service exposes interactive docs:

- Auth Service: `http://localhost:8000/docs`
- Discussion Service: `http://localhost:8001/docs`
- Realtime Service: `http://localhost:8002/docs`
- Notification Service: `http://localhost:8003/docs`

OpenAPI JSON exports are available in:

- `backend/openapi/auth_service.openapi.json`
- `backend/openapi/discussion_service.openapi.json`
- `backend/openapi/realtime_service.openapi.json`
- `backend/openapi/notification_service.openapi.json`

Regenerate specs:

```bash
python backend/scripts/export_openapi.py
```

## WebSocket Explanation

The realtime service (`:8002`) validates JWT access tokens from query params and keeps socket rooms in memory.

### Endpoints

- `ws://localhost:8002/ws/threads/{thread_id}?token=<access_token>`
- `ws://localhost:8002/ws/feed?token=<access_token>`
- `ws://localhost:8002/ws/notifications?token=<access_token>`

### Event Flow

1. Discussion service publishes domain events to Redis (`thread_updates`, `discussion_events`).
2. Realtime service subscribes and broadcasts updates to thread rooms, the global feed room, and user notification rooms.
3. Notification service consumes `discussion_events`, persists notifications, and emits `user_notifications` for realtime delivery.

### Typical Realtime Events

- `thread.updated`, `thread.deleted`
- `comment.created`, `comment.updated`, `comment.deleted`
- `thread.like.updated`, `comment.like.updated`
- `thread.liked`, `comment.liked`
- `mention`, `comment.replied`, `thread.commented`

## Database Design Overview

The project uses a shared PostgreSQL schema with SQLAlchemy models across services.

### Core Entities

- `users`
- `roles`
- `user_roles` (many-to-many between users and roles)
- `threads`
- `comments` (self-referencing for nested replies)
- `likes` (polymorphic target: thread or comment)
- `notifications`
- `thread_reports`

## Future Improvements

- Add a dedicated API Gateway service (Kong, Traefik, or Nginx) for unified routing and policy enforcement
- Introduce DB migrations with Alembic instead of startup schema sync
- Isolate per-service databases (database-per-service pattern)
- Add centralized observability (OpenTelemetry, Prometheus, Grafana)
- Add rate limiting and abuse controls for auth/comments/likes
- Add contract tests and load tests for realtime event throughput
- Add CI/CD pipeline with staged deployment environments

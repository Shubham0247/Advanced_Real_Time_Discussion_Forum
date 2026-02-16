# Docker Setup

This setup runs:

- `frontend` on `http://localhost:3000`
- `auth_service` on `http://localhost:8000`
- `discussion_service` on `http://localhost:8001`
- `realtime_service` on `http://localhost:8002`
- `notification_service` on `http://localhost:8003`
- `postgres` on `localhost:5432`
- `redis` on `localhost:6379`

## 1) Prepare env

Copy `.env.docker.example` to `.env.docker` and set a secure `DOCKER_SECRET_KEY`.

This avoids conflicts with your existing local `.env` (which may contain `localhost` DB URLs).

## 2) Build and start

```bash
docker compose --env-file .env.docker up --build
```

## 3) Stop

```bash
docker compose --env-file .env.docker down
```

To also remove volumes:

```bash
docker compose --env-file .env.docker down -v
```

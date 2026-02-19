# Frontend API Contract (OpenAPI-Oriented)

This document is a compact integration guide for frontend development.  
For exact schemas, use each service's OpenAPI JSON.

## Base Services

- Auth Service: `http://localhost:8000`
- Discussion Service: `http://localhost:8001`
- Realtime Service: `http://localhost:8002`
- Notification Service: `http://localhost:8003`

## Auth Header

All protected REST endpoints require:

`Authorization: Bearer <access_token>`

---

## Auth Service

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
  - Reset flow now uses email OTP.
  - `forgot-password` body: `{ "email": "user@example.com" }`
  - `reset-password` body: `{ "email": "user@example.com", "otp": "123456", "new_password": "..." }`

### Users

- `GET /users/me`
- `PATCH /users/me`
- `GET /users/admin/list?page=&size=&q=&role=` (admin)
- `PATCH /users/{user_id}/status` (admin)
- `POST /users/{user_id}/promote?role_name=` (admin)
- `POST /users/{user_id}/demote?role_name=` (admin)

---

## Discussion Service

### Threads

- `POST /threads/`
- `GET /threads/?page=&size=`
- `GET /threads/search?q=&page=&size=`
- `GET /threads/{thread_id}`
- `PATCH /threads/{thread_id}`
- `DELETE /threads/{thread_id}`

### Comments

- `POST /comments/thread/{thread_id}`
- `GET /comments/thread/{thread_id}`
- `GET /comments/search?q=&page=&size=`
- `PATCH /comments/{comment_id}`
- `DELETE /comments/{comment_id}`

### Likes

- `POST /likes/thread/{thread_id}`
- `POST /likes/comment/{comment_id}`

### Moderation

- `GET /moderation/threads?q=&page=&size=` (admin/moderator)
- `GET /moderation/comments?q=&page=&size=` (admin/moderator)

---

## Notification Service

- `GET /notifications/me?page=&size=`
- `GET /notifications/unread-count`
- `PATCH /notifications/{notification_id}/read`
- `PATCH /notifications/read-all`

---

## Realtime Service (WebSocket)

- `ws://localhost:8002/ws/threads/{thread_id}?token=<access_token>`
- `ws://localhost:8002/ws/notifications?token=<access_token>`

---

## Realtime Event Notes

Published event envelope includes:

- `event_id`
- `event`
- `thread_id`
- `actor_id`
- `payload`
- `timestamp`

Common events:

- `thread.updated`, `thread.deleted`
- `comment.created`, `comment.updated`, `comment.deleted`
- `thread.like.updated`, `comment.like.updated`
- `thread.liked`
- `mention`
- `comment.replied`

---

## OpenAPI Sources

After running export (below), use:

- `backend/openapi/auth_service.openapi.json`
- `backend/openapi/discussion_service.openapi.json`
- `backend/openapi/notification_service.openapi.json`
- `backend/openapi/realtime_service.openapi.json`

---

## Generate OpenAPI Specs

From repo root:

```bash
python backend/scripts/export_openapi.py
```

This writes all service OpenAPI specs to `backend/openapi/`.

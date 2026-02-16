from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os
from sqlalchemy import text

from backend.shared.database.engine import engine
from backend.shared.database.base import Base
from backend.shared.logging.logger import setup_logging
from backend.services.discussion_service.app.api.health import router as health_router
from backend.services.discussion_service.app.api.threads import router as threads_router
from backend.services.discussion_service.app.api import router as comments_router
from backend.services.discussion_service.app.api.likes import router as likes_router
from backend.services.discussion_service.app.api.moderation import router as moderation_router


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        with engine.connect():
            print("Discussion service DB connection successful.")

        Base.metadata.create_all(bind=engine)
        # Lightweight schema sync for local/dev where migrations are not set up.
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE threads ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)")
            )
            connection.execute(
                text(
                    "ALTER TABLE threads ADD COLUMN IF NOT EXISTS moderation_status "
                    "VARCHAR(30) NOT NULL DEFAULT 'pending'"
                )
            )
            connection.execute(
                text(
                    "UPDATE threads SET moderation_status = 'pending' "
                    "WHERE moderation_status IS NULL"
                )
            )
            connection.execute(
                text(
                    """
                    CREATE OR REPLACE VIEW user_activity_view AS
                    SELECT
                        t.author_id AS user_id,
                        'thread.created'::VARCHAR AS activity_type,
                        t.id AS thread_id,
                        NULL::uuid AS comment_id,
                        t.title AS title,
                        LEFT(t.description, 200) AS preview,
                        t.created_at AS created_at
                    FROM threads t
                    WHERE t.is_deleted = FALSE

                    UNION ALL

                    SELECT
                        c.author_id AS user_id,
                        CASE
                            WHEN c.parent_id IS NULL THEN 'comment.created'
                            ELSE 'reply.created'
                        END::VARCHAR AS activity_type,
                        c.thread_id AS thread_id,
                        c.id AS comment_id,
                        t.title AS title,
                        LEFT(c.content, 200) AS preview,
                        c.created_at AS created_at
                    FROM comments c
                    JOIN threads t ON t.id = c.thread_id
                    WHERE c.is_deleted = FALSE
                      AND t.is_deleted = FALSE

                    UNION ALL

                    SELECT
                        l.user_id AS user_id,
                        CASE
                            WHEN l.thread_id IS NOT NULL THEN 'thread.liked'
                            ELSE 'comment.liked'
                        END::VARCHAR AS activity_type,
                        COALESCE(l.thread_id, c.thread_id) AS thread_id,
                        l.comment_id AS comment_id,
                        t.title AS title,
                        CASE
                            WHEN l.thread_id IS NOT NULL THEN 'Liked a thread'
                            ELSE CONCAT('Liked comment: ', LEFT(c.content, 120))
                        END AS preview,
                        l.created_at AS created_at
                    FROM likes l
                    LEFT JOIN comments c ON c.id = l.comment_id
                    JOIN threads t ON t.id = COALESCE(l.thread_id, c.thread_id)
                    WHERE t.is_deleted = FALSE
                      AND (
                        l.thread_id IS NOT NULL OR
                        (c.id IS NOT NULL AND c.is_deleted = FALSE)
                      )
                    """
                )
            )
        print("Discussion tables checked/created.")

    except Exception as e:
        print("Startup error in discussion service:", e)

    yield

    print("Discussion service shutting down...")


setup_logging("discussion_service")

app = FastAPI(
    title="Discussion Service",
    description="Handles threads, comments and likes",
    version="1.0.0",
    lifespan=lifespan,
)

uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(threads_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(moderation_router)

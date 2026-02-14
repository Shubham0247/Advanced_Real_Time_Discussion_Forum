from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.shared.database.engine import engine
from backend.shared.database.base import Base
from backend.shared.logging.logger import setup_logging
from backend.services.discussion_service.app.api.health import router as health_router
from backend.services.discussion_service.app.api.threads import router as threads_router
from backend.services.discussion_service.app.api import router as comments_router
from backend.services.discussion_service.app.api.likes import router as likes_router
from backend.services.discussion_service.app.api.moderation import router as moderation_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        with engine.connect():
            print("Discussion service DB connection successful.")

        Base.metadata.create_all(bind=engine)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(threads_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(moderation_router)
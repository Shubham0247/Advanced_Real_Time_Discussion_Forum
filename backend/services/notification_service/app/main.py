from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from backend.services.notification_service.app.core.redis_listener import start_notification_listener
from backend.services.notification_service.app.models.notification import Notification
from backend.services.notification_service.app.api.notifications import router as notifications_router
from backend.shared.database.base import Base
from backend.shared.database.engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect():
        Base.metadata.create_all(bind=engine)

    listener_task = asyncio.create_task(start_notification_listener())
    try:
        yield
    finally:
        listener_task.cancel()


app = FastAPI(
    title="Notification Service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications_router)

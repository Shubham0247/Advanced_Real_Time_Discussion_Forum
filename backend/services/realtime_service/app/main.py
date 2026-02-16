from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import os

from backend.services.realtime_service.app.websocket.routes import router as ws_router
from backend.services.realtime_service.app.core.redis import start_redis_listener

logger = logging.getLogger("realtime_service")
logging.basicConfig(level=logging.INFO)


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Redis listener started successfully.")

    task = asyncio.create_task(start_redis_listener())
    yield
    
    logger.info("Shutting down Realtime Service...")
    task.cancel()


app = FastAPI(
    title="Realtime Service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)

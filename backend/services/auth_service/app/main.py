import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.auth_service.app.api.health import router as health_router
from backend.services.auth_service.app.core.config import settings
from backend.shared.logging.logger import setup_logging
from backend.shared.database.engine import engine
from backend.services.auth_service.app.api.auth import router as auth_router
from backend.shared.database.base import Base
from backend.services.auth_service.app.api.users import router as users_router
from backend.shared.database.session import SessionLocal
from backend.services.auth_service.app.core.seed import seed_roles

setup_logging(settings.service_name, debug=settings.debug)


logger = logging.getLogger(__name__)


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        with engine.connect():
            logger.info("Database connection successful.")

            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")

            db = SessionLocal()
            seed_roles(db)
            db.close()

            print("Roles seeded successfully.")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error("Database connection failed: %s", exc)

    yield

    logger.info("Auth service shutting down...")

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
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
app.include_router(auth_router)
app.include_router(users_router)

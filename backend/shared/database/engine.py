from sqlalchemy import create_engine
from backend.services.auth_service.app.core.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    echo = settings.debug
)
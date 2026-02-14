from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from backend.shared.database.engine import engine

SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False,
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
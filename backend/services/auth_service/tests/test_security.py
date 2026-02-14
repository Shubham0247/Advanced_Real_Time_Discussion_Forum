import os
from datetime import timedelta
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

from backend.services.auth_service.app.core.security import (  # noqa: E402
    create_access_token,
    create_new_access_token_from_refresh,
    create_refresh_token,
    decode_token,
)


def test_create_access_token_sets_access_type():
    token = create_access_token(
        data={"sub": str(uuid4())},
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_token(token)

    assert payload["type"] == "access"
    assert "sub" in payload


def test_refresh_token_can_issue_new_access_token():
    user_id = str(uuid4())
    refresh = create_refresh_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=20),
    )

    new_access = create_new_access_token_from_refresh(refresh)
    payload = decode_token(new_access)

    assert payload["sub"] == user_id
    assert payload["type"] == "access"

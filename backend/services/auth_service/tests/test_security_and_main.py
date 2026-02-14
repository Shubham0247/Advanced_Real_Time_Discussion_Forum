import asyncio
import os
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

from backend.services.auth_service.app.core import security  # noqa: E402
from backend.services.auth_service.app.main import app, lifespan  # noqa: E402


def test_get_current_user_happy_path(monkeypatch):
    uid = str(uuid4())
    user = SimpleNamespace(id=uid, roles=[])

    monkeypatch.setattr(
        security.jwt,
        "decode",
        lambda *_args, **_kwargs: {"sub": uid, "type": "access"},
    )

    class FakeRepo:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return user

    monkeypatch.setattr(security, "UserRepository", FakeRepo)
    creds = SimpleNamespace(credentials="token")
    assert security.get_current_user(credentials=creds, db=object()) is user


def test_get_current_user_invalid_and_not_found(monkeypatch):
    monkeypatch.setattr(
        security.jwt,
        "decode",
        lambda *_args, **_kwargs: {"sub": None, "type": "access"},
    )
    with pytest.raises(HTTPException) as e1:
        security.get_current_user(credentials=SimpleNamespace(credentials="x"), db=object())
    assert e1.value.status_code == 401

    monkeypatch.setattr(
        security.jwt,
        "decode",
        lambda *_args, **_kwargs: {"sub": str(uuid4()), "type": "access"},
    )

    class RepoNone:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return None

    monkeypatch.setattr(security, "UserRepository", RepoNone)
    with pytest.raises(HTTPException) as e2:
        security.get_current_user(credentials=SimpleNamespace(credentials="x"), db=object())
    assert e2.value.status_code == 401


def test_get_current_user_expired_and_invalid_token(monkeypatch):
    def raise_expired(*_args, **_kwargs):
        raise security.jwt.ExpiredSignatureError("expired")

    monkeypatch.setattr(security.jwt, "decode", raise_expired)
    with pytest.raises(HTTPException) as e1:
        security.get_current_user(credentials=SimpleNamespace(credentials="x"), db=object())
    assert e1.value.detail == "Token expired"

    def raise_invalid(*_args, **_kwargs):
        raise security.jwt.InvalidTokenError("invalid")

    monkeypatch.setattr(security.jwt, "decode", raise_invalid)
    with pytest.raises(HTTPException) as e2:
        security.get_current_user(credentials=SimpleNamespace(credentials="x"), db=object())
    assert e2.value.detail == "Invalid token"


def test_require_roles_allows_and_denies():
    dep = security.require_roles(["admin"])
    dep_ok = dep(current_user=SimpleNamespace(roles=[SimpleNamespace(name="admin")]))
    assert dep_ok.roles[0].name == "admin"

    with pytest.raises(HTTPException) as e:
        dep(current_user=SimpleNamespace(roles=[SimpleNamespace(name="member")]))
    assert e.value.status_code == 403


def test_refresh_token_invalid_type_and_decode_errors(monkeypatch):
    monkeypatch.setattr(security.jwt, "decode", lambda *_args, **_kwargs: {"sub": "u1", "type": "access"})
    with pytest.raises(HTTPException) as e1:
        security.create_new_access_token_from_refresh("r")
    assert e1.value.detail == "Invalid refresh token"

    def raise_expired(*_args, **_kwargs):
        raise security.jwt.ExpiredSignatureError("expired")

    monkeypatch.setattr(security.jwt, "decode", raise_expired)
    with pytest.raises(HTTPException) as e2:
        security.create_new_access_token_from_refresh("r")
    assert e2.value.detail == "Refresh token expired"

    def raise_invalid(*_args, **_kwargs):
        raise security.jwt.InvalidTokenError("invalid")

    monkeypatch.setattr(security.jwt, "decode", raise_invalid)
    with pytest.raises(HTTPException) as e3:
        security.create_new_access_token_from_refresh("r")
    assert e3.value.detail == "Invalid refresh token"


def test_password_reset_token_happy_path():
    uid = str(uuid4())
    token = security.create_password_reset_token(
        data={"sub": uid},
        expires_delta=security.timedelta(minutes=5),
    )
    out_uid = security.get_user_id_from_reset_token(token)
    assert out_uid == uid


def test_password_reset_token_invalid_type_and_errors(monkeypatch):
    monkeypatch.setattr(
        security.jwt,
        "decode",
        lambda *_args, **_kwargs: {"sub": "u1", "type": "access"},
    )
    with pytest.raises(HTTPException) as e1:
        security.get_user_id_from_reset_token("x")
    assert e1.value.detail == "Invalid reset token"

    def raise_expired(*_args, **_kwargs):
        raise security.jwt.ExpiredSignatureError("expired")

    monkeypatch.setattr(security.jwt, "decode", raise_expired)
    with pytest.raises(HTTPException) as e2:
        security.get_user_id_from_reset_token("x")
    assert e2.value.detail == "Reset token expired"

    def raise_invalid(*_args, **_kwargs):
        raise security.jwt.InvalidTokenError("invalid")

    monkeypatch.setattr(security.jwt, "decode", raise_invalid)
    with pytest.raises(HTTPException) as e3:
        security.get_user_id_from_reset_token("x")
    assert e3.value.detail == "Invalid reset token"


def test_lifespan_success_and_exception_paths(monkeypatch):
    class ConnectCtx:
        def __enter__(self):
            return object()

        def __exit__(self, *_args):
            return False

    class GoodEngine:
        def connect(self):
            return ConnectCtx()

    class FakeMeta:
        def __init__(self):
            self.called = False

        def create_all(self, **_kwargs):
            self.called = True

    class FakeBase:
        metadata = FakeMeta()

    class FakeSession:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    seeded = {"called": False}

    def fake_seed(_db):
        seeded["called"] = True

    monkeypatch.setattr("backend.services.auth_service.app.main.engine", GoodEngine())
    monkeypatch.setattr("backend.services.auth_service.app.main.Base", FakeBase)
    monkeypatch.setattr("backend.services.auth_service.app.main.SessionLocal", lambda: FakeSession())
    monkeypatch.setattr("backend.services.auth_service.app.main.seed_roles", fake_seed)

    async def _run_success():
        async with lifespan(app):
            return

    asyncio.run(_run_success())
    assert FakeBase.metadata.called is True
    assert seeded["called"] is True

    class BadEngine:
        def connect(self):
            raise RuntimeError("db down")

    monkeypatch.setattr("backend.services.auth_service.app.main.engine", BadEngine())

    async def _run_error():
        async with lifespan(app):
            return

    asyncio.run(_run_error())

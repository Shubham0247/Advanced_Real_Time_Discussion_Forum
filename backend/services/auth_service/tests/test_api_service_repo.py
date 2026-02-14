import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")

from backend.services.auth_service.app.api import auth as auth_api  # noqa: E402
from backend.services.auth_service.app.api import users as users_api  # noqa: E402
from backend.services.auth_service.app.api.health import health_check  # noqa: E402
from backend.services.auth_service.app.models.role import Role  # noqa: E402
from backend.services.auth_service.app.models.user import User  # noqa: E402
from backend.services.auth_service.app.repositories.user_repository import UserRepository  # noqa: E402
from backend.services.auth_service.app.schemas.user import (  # noqa: E402
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    RoleRead,
    TokenResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from backend.services.auth_service.app.services.user_service import UserService  # noqa: E402


def test_health_endpoint_function():
    assert health_check() == {"status": "auth service running"}


def test_auth_register_login_refresh(monkeypatch):
    class FakeUserService:
        def __init__(self, _db):
            pass

        def create_user(self, _data):
            return {"ok": True}

        def login_user(self, _email, _password):
            return "acc", "ref"

    monkeypatch.setattr(auth_api, "UserService", FakeUserService)
    monkeypatch.setattr(auth_api, "create_new_access_token_from_refresh", lambda _r: "new-token")

    out_register = auth_api.register(
        UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice A",
            password="password123",
        ),
        db=object(),
    )
    out_login = auth_api.login(
        LoginRequest(email="alice@example.com", password="password123"),
        db=object(),
    )
    out_refresh = auth_api.refresh_token(RefreshRequest(refresh_token="r1"))

    assert out_register == {"ok": True}
    assert out_login.access_token == "acc"
    assert out_login.refresh_token == "ref"
    assert out_refresh["access_token"] == "new-token"


def test_auth_register_login_errors(monkeypatch):
    class FakeUserService:
        def __init__(self, _db):
            pass

        def create_user(self, _data):
            raise ValueError("boom")

        def login_user(self, _email, _password):
            raise ValueError("nope")

    monkeypatch.setattr(auth_api, "UserService", FakeUserService)

    with pytest.raises(HTTPException) as e1:
        auth_api.register(
            UserCreate(
                username="alice",
                email="alice@example.com",
                full_name="Alice A",
                password="password123",
            ),
            db=object(),
        )
    assert e1.value.status_code == 400

    with pytest.raises(HTTPException) as e2:
        auth_api.login(
            LoginRequest(email="alice@example.com", password="password123"),
            db=object(),
        )
    assert e2.value.status_code == 401


def test_auth_forgot_password_and_reset(monkeypatch):
    class FakeUserService:
        def __init__(self, _db):
            pass

        def request_password_reset(self, _email):
            return "reset-token-123"

        def reset_password(self, _token, _new_password):
            return None

    monkeypatch.setattr(auth_api, "UserService", FakeUserService)

    out_forgot = auth_api.forgot_password(
        ForgotPasswordRequest(email="alice@example.com"),
        db=object(),
    )
    out_reset = auth_api.reset_password(
        ResetPasswordRequest(reset_token="reset-token-123", new_password="newpassword123"),
        db=object(),
    )

    assert out_forgot.reset_token == "reset-token-123"
    assert "message" in out_reset


def test_auth_reset_password_errors(monkeypatch):
    class FakeUserService:
        def __init__(self, _db):
            pass

        def reset_password(self, _token, _new_password):
            raise ValueError("Invalid reset token")

    monkeypatch.setattr(auth_api, "UserService", FakeUserService)

    with pytest.raises(HTTPException) as e:
        auth_api.reset_password(
            ResetPasswordRequest(reset_token="bad", new_password="newpassword123"),
            db=object(),
        )
    assert e.value.status_code == 400


def test_users_me_and_promote_paths(monkeypatch):
    current_user = SimpleNamespace(id=uuid4(), roles=[SimpleNamespace(name="admin")])
    assert users_api.get_me(current_user=current_user) is current_user

    role_obj = SimpleNamespace(name="moderator")

    class FakeUserRepo:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return SimpleNamespace(roles=[])

    class FakeExec:
        def __init__(self, role):
            self._role = role

        def scalar_one_or_none(self):
            return self._role

    class FakeDB:
        def __init__(self):
            self.committed = False

        def execute(self, _query):
            return FakeExec(role_obj)

        def commit(self):
            self.committed = True

    monkeypatch.setattr(users_api, "UserRepository", FakeUserRepo)
    db = FakeDB()
    out = users_api.promote_user(uuid4(), "moderator", db=db, current_user=current_user)
    assert out["message"] == "User promoted to moderator"
    assert db.committed is True


def test_users_update_me_partial_fields():
    user = SimpleNamespace(
        full_name="Old Name",
        avatar_url="http://old.avatar",
        bio="old bio",
    )

    class FakeDB:
        def __init__(self):
            self.committed = 0
            self.refreshed = 0

        def commit(self):
            self.committed += 1

        def refresh(self, obj):
            assert obj is user
            self.refreshed += 1

    db = FakeDB()
    updated = users_api.update_me(
        user_data=UserUpdate(full_name="New Name"),
        db=db,
        current_user=user,
    )

    assert updated is user
    assert user.full_name == "New Name"
    assert user.avatar_url == "http://old.avatar"
    assert user.bio == "old bio"
    assert db.committed == 1
    assert db.refreshed == 1


def test_users_update_me_empty_payload_keeps_values():
    user = SimpleNamespace(
        full_name="Current Name",
        avatar_url=None,
        bio="current bio",
    )

    class FakeDB:
        def __init__(self):
            self.committed = 0
            self.refreshed = 0

        def commit(self):
            self.committed += 1

        def refresh(self, obj):
            assert obj is user
            self.refreshed += 1

    db = FakeDB()
    users_api.update_me(
        user_data=UserUpdate(),
        db=db,
        current_user=user,
    )

    assert user.full_name == "Current Name"
    assert user.avatar_url is None
    assert user.bio == "current bio"
    assert db.committed == 1
    assert db.refreshed == 1


def test_users_update_me_allows_nullable_fields():
    user = SimpleNamespace(
        full_name="Name",
        avatar_url="http://avatar",
        bio="bio",
    )

    class FakeDB:
        def commit(self):
            return None

        def refresh(self, obj):
            assert obj is user

    users_api.update_me(
        user_data=UserUpdate(avatar_url=None, bio=None),
        db=FakeDB(),
        current_user=user,
    )

    assert user.avatar_url is None
    assert user.bio is None


def test_users_promote_not_found_and_already_has_role(monkeypatch):
    class RepoNone:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return None

    monkeypatch.setattr(users_api, "UserRepository", RepoNone)
    with pytest.raises(HTTPException) as e1:
        users_api.promote_user(uuid4(), "moderator", db=object(), current_user=object())
    assert e1.value.status_code == 404

    role_obj = SimpleNamespace(name="moderator")

    class RepoWithRole:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return SimpleNamespace(roles=[role_obj])

    class FakeExec:
        def scalar_one_or_none(self):
            return role_obj

    class FakeDB:
        def execute(self, _query):
            return FakeExec()

        def commit(self):
            raise AssertionError("Should not commit for already-has-role path")

    monkeypatch.setattr(users_api, "UserRepository", RepoWithRole)
    out = users_api.promote_user(uuid4(), "moderator", db=FakeDB(), current_user=object())
    assert out["message"] == "User already has this role"


def test_users_demote_success(monkeypatch):
    role_obj = SimpleNamespace(name="moderator")
    target_user = SimpleNamespace(roles=[role_obj])

    class FakeUserRepo:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return target_user

    class FakeExec:
        def scalar_one_or_none(self):
            return role_obj

    class FakeDB:
        def __init__(self):
            self.committed = False

        def execute(self, _query):
            return FakeExec()

        def commit(self):
            self.committed = True

    monkeypatch.setattr(users_api, "UserRepository", FakeUserRepo)
    db = FakeDB()
    out = users_api.demote_user(uuid4(), "moderator", db=db, current_user=object())
    assert out["message"] == "User demoted from moderator"
    assert target_user.roles == []
    assert db.committed is True


def test_users_demote_not_found_or_missing_role(monkeypatch):
    class RepoNone:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return None

    monkeypatch.setattr(users_api, "UserRepository", RepoNone)
    with pytest.raises(HTTPException) as e1:
        users_api.demote_user(uuid4(), "moderator", db=object(), current_user=object())
    assert e1.value.status_code == 404

    role_obj = SimpleNamespace(name="moderator")
    target_user = SimpleNamespace(roles=[])

    class RepoWithUser:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return target_user

    class FakeExec:
        def scalar_one_or_none(self):
            return role_obj

    class FakeDB:
        def execute(self, _query):
            return FakeExec()

        def commit(self):
            raise AssertionError("Should not commit when user lacks role")

    monkeypatch.setattr(users_api, "UserRepository", RepoWithUser)
    out = users_api.demote_user(uuid4(), "moderator", db=FakeDB(), current_user=object())
    assert out["message"] == "User does not have this role"


def test_users_demote_role_not_found(monkeypatch):
    class RepoWithUser:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return SimpleNamespace(roles=[])

    class FakeExec:
        def scalar_one_or_none(self):
            return None

    class FakeDB:
        def execute(self, _query):
            return FakeExec()

    monkeypatch.setattr(users_api, "UserRepository", RepoWithUser)
    with pytest.raises(HTTPException) as e:
        users_api.demote_user(uuid4(), "moderator", db=FakeDB(), current_user=object())
    assert e.value.status_code == 404


def test_users_admin_list_endpoint(monkeypatch):
    fake_items = [SimpleNamespace(id=uuid4())]

    class FakeRepo:
        def __init__(self, _db):
            pass

        def list_users(self, **kwargs):
            assert kwargs["skip"] == 0
            assert kwargs["limit"] == 20
            assert kwargs["q"] == "ali"
            assert kwargs["role"] == "member"
            return fake_items

        def count_users(self, **kwargs):
            assert kwargs["q"] == "ali"
            assert kwargs["role"] == "member"
            return 1

    monkeypatch.setattr(users_api, "UserRepository", FakeRepo)
    out = users_api.list_users_admin(
        page=1,
        size=20,
        q="ali",
        role="member",
        db=object(),
        current_user=object(),
    )
    assert out["total"] == 1
    assert out["items"] == fake_items


def test_users_update_status_endpoint(monkeypatch):
    user = SimpleNamespace(id=uuid4(), is_active=True)

    class FakeRepo:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return user

    class FakeDB:
        def __init__(self):
            self.committed = 0
            self.refreshed = 0

        def commit(self):
            self.committed += 1

        def refresh(self, obj):
            assert obj is user
            self.refreshed += 1

    monkeypatch.setattr(users_api, "UserRepository", FakeRepo)
    db = FakeDB()
    out = users_api.update_user_status(
        user_id=user.id,
        status_data=SimpleNamespace(is_active=False),
        db=db,
        current_user=object(),
    )
    assert out["is_active"] is False
    assert db.committed == 1
    assert db.refreshed == 1


def test_users_update_status_not_found(monkeypatch):
    class FakeRepo:
        def __init__(self, _db):
            pass

        def get_by_id(self, _uid):
            return None

    monkeypatch.setattr(users_api, "UserRepository", FakeRepo)
    with pytest.raises(HTTPException) as e:
        users_api.update_user_status(
            user_id=uuid4(),
            status_data=SimpleNamespace(is_active=False),
            db=object(),
            current_user=object(),
        )
    assert e.value.status_code == 404


def test_user_repository_list_and_count_users():
    rows = [object(), object()]

    class FakeScalars:
        def __iter__(self):
            return iter(rows)

    class FakeDB:
        def scalars(self, _query):
            return FakeScalars()

        def scalar(self, _query):
            return 2

    repo = UserRepository(FakeDB())
    listed = repo.list_users(skip=0, limit=20, q="ali", role="member")
    total = repo.count_users(q="ali", role="member")

    assert listed == rows
    assert total == 2


def test_user_repository_methods():
    calls = {"add": 0, "commit": 0, "refresh": 0, "scalar": 0}
    sentinel = object()

    class FakeDB:
        def add(self, _user):
            calls["add"] += 1

        def commit(self):
            calls["commit"] += 1

        def refresh(self, _user):
            calls["refresh"] += 1

        def scalar(self, _query):
            calls["scalar"] += 1
            return sentinel

    repo = UserRepository(FakeDB())
    user = User(
        username="a",
        email="a@a.com",
        hashed_password="x",
        full_name="A",
        avatar_url=None,
        bio=None,
    )

    assert repo.create(user) is user
    assert repo.get_by_id(uuid4()) is sentinel
    assert repo.get_by_email("a@a.com") is sentinel
    assert repo.get_by_username("a") is sentinel
    assert calls == {"add": 1, "commit": 1, "refresh": 1, "scalar": 3}


def test_user_service_create_auth_and_login(monkeypatch):
    member_role = Role(name="member", description="Regular user")

    class FakeExec:
        def scalar_one(self):
            return member_role

    class FakeDB:
        def execute(self, _query):
            return FakeExec()

    class FakeRepo:
        def __init__(self):
            self.created_user = None

        def get_by_email(self, _email):
            return None

        def get_by_username(self, _username):
            return None

        def create(self, user):
            self.created_user = user
            user.id = uuid4()
            return user

    service = UserService(FakeDB())
    fake_repo = FakeRepo()
    service.user_repo = fake_repo
    monkeypatch.setattr(service, "_hash_password", lambda _p: "HASHED")
    monkeypatch.setattr(service, "authenticate_user", lambda _e, _p: SimpleNamespace(id=uuid4()))
    monkeypatch.setattr("backend.services.auth_service.app.services.user_service.create_access_token", lambda **kwargs: "A")
    monkeypatch.setattr("backend.services.auth_service.app.services.user_service.create_refresh_token", lambda **kwargs: "R")

    created = service.create_user(
        UserCreate(
            username="Alice",
            email="Alice@example.com",
            full_name="Alice A",
            password="password123",
        )
    )
    access, refresh = service.login_user("alice@example.com", "password123")

    assert created.hashed_password == "HASHED"
    assert len(created.roles) == 1
    assert created.roles[0] is member_role
    assert (access, refresh) == ("A", "R")


def test_user_service_duplicate_and_invalid_login_paths(monkeypatch):
    class FakeDB:
        def execute(self, _query):
            raise AssertionError("Should not hit DB execute on duplicate checks")

    service = UserService(FakeDB())
    service.user_repo = SimpleNamespace(
        get_by_email=lambda _e: object(),
        get_by_username=lambda _u: None,
    )

    with pytest.raises(ValueError):
        service.create_user(
            UserCreate(
                username="alice",
                email="alice@example.com",
                full_name="Alice A",
                password="password123",
            )
        )

    service.authenticate_user = lambda _e, _p: None
    with pytest.raises(ValueError):
        service.login_user("a@a.com", "x")


def test_user_service_authenticate_user_paths():
    user = SimpleNamespace(hashed_password="h")
    service = UserService(SimpleNamespace())
    service.user_repo = SimpleNamespace(get_by_email=lambda _e: user)
    service.verify_password = lambda _p, _h: True
    assert service.authenticate_user("a@a.com", "p") is user

    service.verify_password = lambda _p, _h: False
    assert service.authenticate_user("a@a.com", "p") is None

    service.user_repo = SimpleNamespace(get_by_email=lambda _e: None)
    assert service.authenticate_user("a@a.com", "p") is None


def test_user_service_password_reset_paths(monkeypatch):
    user = SimpleNamespace(id=uuid4(), hashed_password="old-hash")

    class FakeDB:
        def __init__(self):
            self.commits = 0
            self.refreshed = 0

        def commit(self):
            self.commits += 1

        def refresh(self, obj):
            assert obj is user
            self.refreshed += 1

    service = UserService(FakeDB())
    service.user_repo = SimpleNamespace(
        get_by_email=lambda _e: user,
        get_by_id=lambda _uid: user,
    )
    monkeypatch.setattr(
        "backend.services.auth_service.app.services.user_service.create_password_reset_token",
        lambda **_kwargs: "reset-token",
    )
    monkeypatch.setattr(
        "backend.services.auth_service.app.services.user_service.get_user_id_from_reset_token",
        lambda _token: str(user.id),
    )
    monkeypatch.setattr(service, "_hash_password", lambda _p: "new-hash")

    token = service.request_password_reset("alice@example.com")
    service.reset_password("reset-token", "newpassword123")

    assert token == "reset-token"
    assert user.hashed_password == "new-hash"
    assert service.db.commits == 1
    assert service.db.refreshed == 1

    service.user_repo = SimpleNamespace(get_by_email=lambda _e: None, get_by_id=lambda _uid: None)
    assert service.request_password_reset("missing@example.com") is None

    with pytest.raises(ValueError):
        service.reset_password("bad-token", "newpassword123")


def test_user_schema_models_construct():
    now = datetime.now(timezone.utc)
    role = RoleRead(id=uuid4(), name="member", description=None)
    read = UserRead(
        id=uuid4(),
        username="alice",
        email="alice@example.com",
        full_name="Alice A",
        avatar_url=None,
        bio=None,
        is_active=True,
        created_at=now,
        updated_at=now,
        roles=[role],
    )
    token = TokenResponse(access_token="a", refresh_token="r")
    update = UserUpdate(full_name="Alice Updated")

    assert read.roles[0].name == "member"
    assert token.token_type == "bearer"
    assert update.full_name == "Alice Updated"

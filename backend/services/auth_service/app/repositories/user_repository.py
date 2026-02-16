from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from backend.services.auth_service.app.models.user import User
from backend.services.auth_service.app.models.role import Role


# SQLAlchemy's func.* is dynamically generated; pylint can't infer callability.
# pylint: disable=not-callable
class UserRepository:
    """
    Handles database operations related to User entity
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id) -> User | None:

        query = select(User).where(User.id == user_id)
        return self.db.scalar(query)

    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return self.db.scalar(query)

    def get_by_email_or_username(self, identifier: str) -> User | None:
        normalized = identifier.strip().lower()
        query = select(User).where(
            or_(
                func.lower(User.email) == normalized,
                func.lower(User.username) == normalized,
            )
        )
        return self.db.scalar(query)

    def get_by_username(self, username: str) -> User | None:

        query = select(User).where(User.username == username)
        return self.db.scalar(query)

    def list_users(
        self,
        *,
        skip: int,
        limit: int,
        q: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        query = select(User)

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )

        if role:
            query = query.where(User.roles.any(Role.name == role.strip().lower()))

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(query))

    def count_users(self, *, q: str | None = None, role: str | None = None) -> int:
        query = select(func.count()).select_from(User)

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )

        if role:
            query = query.where(User.roles.any(Role.name == role.strip().lower()))

        return self.db.scalar(query)

    def search_public_users(self, *, skip: int, limit: int, q: str | None = None) -> list[User]:
        query = select(User).where(User.is_active.is_(True))

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                    User.bio.ilike(pattern),
                )
            )

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(query))

    def count_public_users(self, *, q: str | None = None) -> int:
        query = select(func.count()).select_from(User).where(User.is_active.is_(True))

        if q:
            pattern = f"%{q.strip()}%"
            query = query.where(
                or_(
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                    User.bio.ilike(pattern),
                )
            )

        return self.db.scalar(query)

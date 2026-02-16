from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from sqlalchemy import select

from backend.services.auth_service.app.models.user import User
from backend.services.auth_service.app.repositories.user_repository import UserRepository
from backend.services.auth_service.app.schemas.user import UserCreate
from backend.services.auth_service.app.core.security import(
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    get_user_id_from_reset_token,
)
from datetime import timedelta
from backend.services.auth_service.app.core.config import settings
from backend.services.auth_service.app.models.role import Role


password_hash = PasswordHash.recommended()

class UserService:
    """
    Handles business logic related to users
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def _hash_password(self, password: str)-> str:
        return password_hash.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user after applying business rules.
        """

        username = user_data.username.strip().lower()
        email = user_data.email.strip().lower()

        if self.user_repo.get_by_email(email):
            raise ValueError("Email already registered")
        
        if self.user_repo.get_by_username(username):
            raise ValueError("Username already taken")
        
        hashed_password = self._hash_password(user_data.password)

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=user_data.full_name.strip(),
            avatar_url=user_data.avatar_url,
            bio=user_data.bio,
        )

        member_role = self.db.execute(
            select(Role).where(Role.name == "member")
        ).scalar_one()

        new_user.roles.append(member_role)

        return self.user_repo.create(new_user)

    def authenticate_user(self, email: str, password: str):
        user = self.user_repo.get_by_email_or_username(email)
    
        if not user:
            return None

        if not getattr(user, "is_active", True):
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user
    
    def login_user(self, email: str, password: str):
        user = self.authenticate_user(email, password)

        if not user:
            raise ValueError("Invalid email of password")
        
        access_token = create_access_token(
            data = {"sub":str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=settings.refresh_token_expire_days)
        )

        return access_token, refresh_token

    def request_password_reset(self, email: str) -> str | None:
        user = self.user_repo.get_by_email(email.strip().lower())
        if not user:
            return None

        reset_token = create_password_reset_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.reset_token_expire_minutes),
        )
        return reset_token

    def reset_password(self, reset_token: str, new_password: str) -> None:
        user_id = get_user_id_from_reset_token(reset_token)
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Invalid reset token")

        user.hashed_password = self._hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)

    def change_password(self, user, current_password: str, new_password: str) -> None:
        if not self.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        if current_password == new_password:
            raise ValueError("New password must be different from current password")

        user.hashed_password = self._hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)


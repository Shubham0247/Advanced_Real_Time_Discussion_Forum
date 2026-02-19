import secrets
import string
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.services.auth_service.app.core.config import settings
from backend.services.auth_service.app.core.security import (
    create_access_token,
    create_refresh_token,
)
from backend.services.auth_service.app.models.password_reset_otp import PasswordResetOTP
from backend.services.auth_service.app.models.role import Role
from backend.services.auth_service.app.models.user import User
from backend.services.auth_service.app.repositories.user_repository import UserRepository
from backend.services.auth_service.app.schemas.user import UserCreate
from backend.services.auth_service.app.services.email_service import send_password_reset_otp_email


password_hash = PasswordHash.recommended()

class UserService:
    """
    Handles business logic related to users
    """

    def __init__(self, db: Session):
        """Initialize the user service with a database session and repository."""
        self.db = db
        self.user_repo = UserRepository(db)

    def _hash_password(self, password: str)-> str:
        """Hash a plaintext password using the configured password hasher."""
        return password_hash.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its stored hash."""
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
        """Authenticate an active user by email/username and password."""
        user = self.user_repo.get_by_email_or_username(email)
    
        if not user:
            return None

        if not getattr(user, "is_active", True):
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        return user
    
    def login_user(self, email: str, password: str):
        """Authenticate a user and return access and refresh tokens."""
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

    def _generate_password_reset_otp(self) -> str:
        """Generate a numeric OTP for password reset requests."""
        otp_length = max(settings.password_reset_otp_length, 4)
        return "".join(secrets.choice(string.digits) for _ in range(otp_length))

    def _store_password_reset_otp(self, user_id, otp: str) -> None:
        """Invalidate active OTPs and persist a new password reset OTP."""
        now = datetime.now(timezone.utc)
        active_codes_query = select(PasswordResetOTP).where(
            PasswordResetOTP.user_id == user_id,
            PasswordResetOTP.used_at.is_(None),
        )
        for active_code in self.db.scalars(active_codes_query):
            active_code.used_at = now

        otp_record = PasswordResetOTP(
            user_id=user_id,
            otp_hash=self._hash_password(otp),
            expires_at=now + timedelta(minutes=settings.password_reset_otp_expire_minutes),
        )
        self.db.add(otp_record)
        self.db.commit()

    def _get_latest_password_reset_otp(self, user_id) -> PasswordResetOTP | None:
        """Fetch the most recently created password reset OTP for a user."""
        otp_query = (
            select(PasswordResetOTP)
            .where(PasswordResetOTP.user_id == user_id)
            .order_by(PasswordResetOTP.created_at.desc())
        )
        return self.db.scalar(otp_query)

    def request_password_reset(self, email: str) -> None:
        """Create and send a password reset OTP for an existing user."""
        user = self.user_repo.get_by_email(email.strip().lower())
        if not user:
            return

        otp = self._generate_password_reset_otp()
        self._store_password_reset_otp(user.id, otp)
        send_password_reset_otp_email(user.email, otp)

    def reset_password(self, email: str, otp: str, new_password: str) -> None:
        """Validate an OTP and update the user's password."""
        user = self.user_repo.get_by_email(email.strip().lower())
        if not user:
            raise ValueError("Invalid or expired OTP")

        otp_record = self._get_latest_password_reset_otp(user.id)
        now = datetime.now(timezone.utc)

        if not otp_record or otp_record.used_at is not None:
            raise ValueError("Invalid or expired OTP")

        if otp_record.expires_at <= now:
            raise ValueError("Invalid or expired OTP")

        if otp_record.attempt_count >= settings.password_reset_otp_max_attempts:
            raise ValueError("Invalid or expired OTP")

        if not self.verify_password(otp, otp_record.otp_hash):
            otp_record.attempt_count += 1
            if otp_record.attempt_count >= settings.password_reset_otp_max_attempts:
                otp_record.used_at = now
            self.db.commit()
            raise ValueError("Invalid or expired OTP")

        otp_record.used_at = now
        user.hashed_password = self._hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)

    def change_password(self, user, current_password: str, new_password: str) -> None:
        """Change a user's password after validating the current password."""
        if not self.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        if current_password == new_password:
            raise ValueError("New password must be different from current password")

        user.hashed_password = self._hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.shared.database.session import get_db
from backend.services.auth_service.app.schemas.user import UserCreate, UserRead
from backend.services.auth_service.app.services.user_service import UserService
from backend.services.auth_service.app.schemas.user import LoginRequest, TokenResponse
from backend.services.auth_service.app.schemas.user import RefreshRequest
from backend.services.auth_service.app.schemas.user import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)
from backend.services.auth_service.app.core.security import create_new_access_token_from_refresh

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):

    user_service = UserService(db)

    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

@router.post("/login",response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)

    try:
        access_token, refresh_token_value = user_service.login_user(
            login_data.email,
            login_data.password,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    new_access_token = create_new_access_token_from_refresh(
        data.refresh_token
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)
    reset_token = user_service.request_password_reset(data.email)

    return ForgotPasswordResponse(
        message="If the account exists, a password reset token was generated.",
        reset_token=reset_token,
    )


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user_service = UserService(db)

    try:
        user_service.reset_password(data.reset_token, data.new_password)
    except (ValueError, HTTPException) as exc:
        detail = str(exc) if isinstance(exc, ValueError) else exc.detail
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc

    return {"message": "Password reset successful"}

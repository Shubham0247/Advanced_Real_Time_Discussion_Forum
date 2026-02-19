from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import List
from pydantic import ConfigDict

class UserBase(BaseModel):
    username: str = Field(...,min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    avatar_url: str | None = None
    bio: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)

class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleRead]

    model_config = ConfigDict(from_attributes=True)
    
class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    avatar_url: str | None = None
    bio: str | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str


class UserListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[UserRead]


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=8)


class MentionUserRead(BaseModel):
    id: UUID
    username: str
    full_name: str
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MentionSuggestResponse(BaseModel):
    items: List[MentionUserRead]


class MentionResolveRequest(BaseModel):
    usernames: List[str]


class MentionResolveResponse(BaseModel):
    existing_usernames: List[str]


class UserSearchRead(BaseModel):
    id: UUID
    username: str
    full_name: str
    avatar_url: str | None = None
    bio: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserSearchResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[UserSearchRead]

"""
Authentication request/response schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    id: str = Field(..., min_length=1, max_length=36)
    email_verified: bool = False
    roles: Optional[str] = None


class UserRead(UserBase):
    """User read schema."""

    id: str
    email_verified: bool
    roles: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfo(BaseModel):
    """User info from OIDC userinfo endpoint."""

    sub: str
    email: Optional[EmailStr] = None
    preferred_username: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = None
    realm_access: Optional[dict] = None


class LoginResponse(BaseModel):
    """Login initiation response."""

    auth_url: str
    state: str


class CallbackRequest(BaseModel):
    """OIDC callback request parameters."""

    code: str
    state: str
    session_state: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request."""

    id_token_hint: Optional[str] = None
    post_logout_redirect_uri: Optional[str] = None

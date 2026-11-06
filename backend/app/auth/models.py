"""
Authentication database models.
"""
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """User model for OIDC authenticated users."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Keycloak subject ID
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Token storage (encrypted in production)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # OIDC claims
    email_verified: Mapped[bool] = mapped_column(default=False)
    roles: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of roles

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class OAuthState(Base):
    """OAuth2/PKCE state storage for CSRF protection."""

    __tablename__ = "oauth_states"

    state: Mapped[str] = mapped_column(String(64), primary_key=True)
    code_verifier: Mapped[str] = mapped_column(String(128), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(default=False)

"""
Tests for auth module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import create_app
from app.auth.models import User, OAuthState
from app.auth.service import PKCEService, OIDCClient, AuthService, OIDCError
from app.core.database import get_session, engine, Base


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.database import async_session_maker
    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestPKCEService:
    """Tests for PKCE service."""

    def test_generate_code_verifier(self):
        """Test code verifier generation."""
        verifier = PKCEService.generate_code_verifier()
        assert isinstance(verifier, str)
        assert 43 <= len(verifier) <= 128

    def test_generate_code_challenge(self):
        """Test code challenge generation."""
        verifier = "test_verifier_12345678901234567890"
        challenge = PKCEService.generate_code_challenge(verifier)
        assert isinstance(challenge, str)
        assert len(challenge) > 0

    def test_generate_state(self):
        """Test state generation."""
        state = PKCEService.generate_state()
        assert isinstance(state, str)
        assert len(state) > 0


class TestAuthEndpoints:
    """Tests for auth API endpoints."""

    @pytest.mark.asyncio
    async def test_login_not_configured(self, client: AsyncClient):
        """Test login endpoint when OIDC not configured."""
        response = await client.get("/auth/login?redirect_uri=http://localhost:5173/callback")
        # Should return 503 when OIDC not configured
        assert response.status_code == 503
        data = response.json()
        assert "OIDC not configured" in data["detail"]

    @pytest.mark.asyncio
    async def test_callback_missing_params(self, client: AsyncClient):
        """Test callback endpoint with missing parameters."""
        response = await client.get("/auth/callback")
        assert response.status_code == 422  # Validation error


class TestOIDCClient:
    """Tests for OIDC client."""

    @pytest.mark.asyncio
    async def test_oidc_client_init(self):
        """Test OIDC client initialization."""
        # Test without config
        with patch("app.auth.service.settings") as mock_settings:
            mock_settings.oidc_issuer_url = None
            mock_settings.oidc_client_id = "test-client"
            mock_settings.oidc_client_secret = None

            client = OIDCClient()
            assert client.issuer_url is None
            assert client.client_id == "test-client"


class TestAuthService:
    """Tests for auth service."""

    @pytest.mark.asyncio
    async def test_initiate_login_no_config(self, db_session):
        """Test initiate login without OIDC config."""
        from app.core.config import settings

        # Temporarily remove OIDC config
        original_issuer = settings.oidc_issuer_url
        original_client = settings.oidc_client_id
        settings.oidc_issuer_url = None
        settings.oidc_client_id = None

        try:
            auth_service = AuthService(db_session)
            with pytest.raises(OIDCError, match="OIDC not configured"):
                await auth_service.initiate_login("http://localhost:5173/callback")
        finally:
            settings.oidc_issuer_url = original_issuer
            settings.oidc_client_id = original_client


@pytest.mark.asyncio
async def test_user_model(db_session):
    """Test User model creation."""
    user = User(
        id="test-user-id",
        email="test@example.com",
        username="testuser",
        full_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id == "test-user-id"
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.email_verified is False


@pytest.mark.asyncio
async def test_oauth_state_model(db_session):
    """Test OAuthState model creation."""
    from datetime import datetime, timedelta

    state = OAuthState(
        state="test-state",
        code_verifier="test-verifier",
        redirect_uri="http://localhost:5173/callback",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db_session.add(state)
    await db_session.commit()
    await db_session.refresh(state)

    assert state.state == "test-state"
    assert state.code_verifier == "test-verifier"
    assert state.redirect_uri == "http://localhost:5173/callback"
    assert state.used is False

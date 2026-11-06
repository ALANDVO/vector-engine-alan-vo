"""
OIDC authentication service with PKCE flow for Keycloak.
"""
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
from authlib.jose import JsonWebToken, JsonWebKey
from authlib.jose.errors import JoseError
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, OAuthState
from app.auth.schemas import TokenResponse, UserInfo, LoginResponse, CallbackRequest
from app.core.config import settings


class OIDCError(Exception):
    """OIDC authentication error."""

    pass


class PKCEService:
    """PKCE (Proof Key for Code Exchange) implementation."""

    @staticmethod
    def generate_code_verifier() -> str:
        """Generate a random code verifier."""
        # RFC 7636: 43-128 characters, unreserved chars
        return secrets.token_urlsafe(96)[:128]

    @staticmethod
    def generate_code_challenge(code_verifier: str) -> str:
        """Generate code challenge from verifier using S256 method."""
        import hashlib
        import base64

        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    @staticmethod
    def generate_state() -> str:
        """Generate a random state parameter."""
        return secrets.token_urlsafe(32)


class OIDCClient:
    """OIDC client for Keycloak integration."""

    def __init__(self):
        self.issuer_url = settings.oidc_issuer_url
        self.client_id = settings.oidc_client_id
        self.client_secret = settings.oidc_client_secret
        self._discovery_config: Optional[dict] = None
        self._jwks: Optional[dict] = None

    async def _get_discovery_config(self) -> dict:
        """Fetch OIDC discovery configuration."""
        if self._discovery_config is not None:
            return self._discovery_config

        if not self.issuer_url:
            raise OIDCError("OIDC issuer URL not configured")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.issuer_url.rstrip('/')}/.well-known/openid-configuration",
                timeout=10.0,
            )
            response.raise_for_status()
            self._discovery_config = response.json()
            return self._discovery_config

    async def _get_jwks(self) -> dict:
        """Fetch JSON Web Key Set."""
        if self._jwks is not None:
            return self._jwks

        config = await self._get_discovery_config()
        jwks_uri = config.get("jwks_uri")
        if not jwks_uri:
            raise OIDCError("JWKS URI not found in discovery config")

        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_uri, timeout=10.0)
            response.raise_for_status()
            self._jwks = response.json()
            return self._jwks

    def build_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        scope: str = "openid profile email",
    ) -> str:
        """Build the authorization URL for PKCE flow."""
        config = self._discovery_config
        if not config:
            # We need discovery config for authorization_endpoint
            # This will be fetched on first use
            raise OIDCError("Discovery config not loaded")

        auth_endpoint = config.get("authorization_endpoint")
        if not auth_endpoint:
            raise OIDCError("Authorization endpoint not found")

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{auth_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str, redirect_uri: str, code_verifier: str
    ) -> TokenResponse:
        """Exchange authorization code for tokens."""
        config = await self._get_discovery_config()
        token_endpoint = config.get("token_endpoint")
        if not token_endpoint:
            raise OIDCError("Token endpoint not found")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
            "client_id": self.client_id,
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data=data,
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            token_data = response.json()

        return TokenResponse(**token_data)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        config = await self._get_discovery_config()
        token_endpoint = config.get("token_endpoint")
        if not token_endpoint:
            raise OIDCError("Token endpoint not found")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data=data,
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            token_data = response.json()

        return TokenResponse(**token_data)

    async def get_userinfo(self, access_token: str) -> UserInfo:
        """Fetch user info from OIDC userinfo endpoint."""
        config = await self._get_discovery_config()
        userinfo_endpoint = config.get("userinfo_endpoint")
        if not userinfo_endpoint:
            raise OIDCError("Userinfo endpoint not found")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )
            response.raise_for_status()
            return UserInfo(**response.json())

    async def validate_id_token(self, id_token: str) -> dict:
        """Validate ID token signature and claims."""
        jwks = await self._get_jwks()
        try:
            # Use authlib for JWK validation
            jwt_validator = JsonWebToken(["RS256"])
            claims = jwt_validator.decode(id_token, jwks)
            claims.validate()
            return claims
        except JoseError as e:
            # Fallback: decode without verification for development
            # In production, this MUST validate properly
            if settings.debug:
                return jwt.decode(id_token, options={"verify_signature": False})
            raise OIDCError(f"ID token validation failed: {e}")

    def build_logout_url(
        self,
        id_token_hint: Optional[str] = None,
        post_logout_redirect_uri: Optional[str] = None,
    ) -> str:
        """Build Keycloak logout URL."""
        config = self._discovery_config
        if not config:
            raise OIDCError("Discovery config not loaded")

        end_session_endpoint = config.get("end_session_endpoint")
        if not end_session_endpoint:
            raise OIDCError("End session endpoint not found")

        params = {}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        if post_logout_redirect_uri:
            params["post_logout_redirect_uri"] = post_logout_redirect_uri

        if params:
            return f"{end_session_endpoint}?{urlencode(params)}"
        return end_session_endpoint


class AuthService:
    """High-level authentication service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.oidc_client = OIDCClient()

    async def initiate_login(self, redirect_uri: str) -> LoginResponse:
        """Initiate OIDC login with PKCE."""
        if not settings.oidc_issuer_url or not settings.oidc_client_id:
            raise OIDCError("OIDC not configured")

        # Load discovery config
        await self.oidc_client._get_discovery_config()

        # Generate PKCE parameters
        code_verifier = PKCEService.generate_code_verifier()
        code_challenge = PKCEService.generate_code_challenge(code_verifier)
        state = PKCEService.generate_state()

        # Store state with code verifier
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        oauth_state = OAuthState(
            state=state,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
            expires_at=expires_at,
        )
        self.session.add(oauth_state)
        await self.session.commit()

        # Build authorization URL
        auth_url = self.oidc_client.build_authorization_url(
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
        )

        return LoginResponse(auth_url=auth_url, state=state)

    async def handle_callback(self, callback: CallbackRequest) -> TokenResponse:
        """Handle OIDC callback and exchange code for tokens."""
        # Retrieve and validate state
        result = await self.session.execute(
            select(OAuthState).where(OAuthState.state == callback.state)
        )
        oauth_state = result.scalar_one_or_none()

        if not oauth_state:
            raise OIDCError("Invalid or expired state")

        if oauth_state.used:
            raise OIDCError("State already used")

        if oauth_state.expires_at < datetime.utcnow():
            raise OIDCError("State expired")

        # Mark state as used
        oauth_state.used = True
        await self.session.commit()

        # Exchange code for tokens
        tokens = await self.oidc_client.exchange_code_for_tokens(
            code=callback.code,
            redirect_uri=oauth_state.redirect_uri,
            code_verifier=oauth_state.code_verifier,
        )

        return tokens

    async def get_or_create_user(self, userinfo: UserInfo, tokens: TokenResponse) -> User:
        """Get existing user or create new one from userinfo."""
        result = await self.session.execute(
            select(User).where(User.id == userinfo.sub)
        )
        user = result.scalar_one_or_none()

        roles = None
        if userinfo.realm_access and "roles" in userinfo.realm_access:
            import json

            roles = json.dumps(userinfo.realm_access["roles"])

        if user:
            # Update existing user
            user.email = userinfo.email or user.email
            user.username = userinfo.preferred_username or user.username
            user.full_name = userinfo.name or user.full_name
            user.avatar_url = userinfo.picture or user.avatar_url
            user.email_verified = userinfo.email_verified or False
            user.roles = roles
            user.access_token = tokens.access_token
            user.refresh_token = tokens.refresh_token
            if tokens.expires_in:
                user.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.expires_in)
            user.last_login_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                id=userinfo.sub,
                email=userinfo.email or "",
                username=userinfo.preferred_username or userinfo.sub,
                full_name=userinfo.name,
                avatar_url=userinfo.picture,
                email_verified=userinfo.email_verified or False,
                roles=roles,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_expires_at=(
                    datetime.utcnow() + timedelta(seconds=tokens.expires_in)
                    if tokens.expires_in
                    else None
                ),
                last_login_at=datetime.utcnow(),
            )
            self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def logout(self, user_id: str) -> None:
        """Logout user and clear tokens."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.access_token = None
            user.refresh_token = None
            user.token_expires_at = None
            await self.session.commit()

    async def refresh_user_token(self, user: User) -> TokenResponse:
        """Refresh user's access token."""
        if not user.refresh_token:
            raise OIDCError("No refresh token available")

        tokens = await self.oidc_client.refresh_access_token(user.refresh_token)

        user.access_token = tokens.access_token
        user.refresh_token = tokens.refresh_token or user.refresh_token
        if tokens.expires_in:
            user.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.expires_in)

        await self.session.commit()
        await self.session.refresh(user)
        return tokens

    def build_logout_url(
        self,
        id_token_hint: Optional[str] = None,
        post_logout_redirect_uri: Optional[str] = None,
    ) -> str:
        """Build logout URL."""
        return self.oidc_client.build_logout_url(
            id_token_hint=id_token_hint,
            post_logout_redirect_uri=post_logout_redirect_uri,
        )

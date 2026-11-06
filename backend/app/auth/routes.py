"""
Authentication API routes for OIDC/PKCE flow.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    LoginResponse,
    CallbackRequest,
    TokenResponse,
    UserRead,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.auth.service import AuthService, OIDCError
from app.auth.models import User
from app.core.database import get_session
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Get auth service instance."""
    return AuthService(session)


@router.get("/login", response_model=LoginResponse)
async def login(
    redirect_uri: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Initiate OIDC login flow with PKCE.

    Returns authorization URL and state parameter.
    Frontend should redirect user to auth_url.
    """
    if not settings.oidc_issuer_url or not settings.oidc_client_id:
        raise HTTPException(
            status_code=503,
            detail="OIDC not configured. Set OIDC_ISSUER_URL and OIDC_CLIENT_ID.",
        )

    try:
        return await auth_service.initiate_login(redirect_uri)
    except OIDCError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    session_state: Optional[str] = Query(None),
    auth_service: AuthService = Depends(get_auth_service),
    request: Request = None,
) -> RedirectResponse:
    """
    OIDC callback endpoint.

    Exchanges authorization code for tokens, creates/updates user,
    and redirects to frontend with tokens.
    """
    callback_request = CallbackRequest(code=code, state=state, session_state=session_state)

    try:
        tokens = await auth_service.handle_callback(callback_request)
        userinfo = await auth_service.oidc_client.get_userinfo(tokens.access_token)
        user = await auth_service.get_or_create_user(userinfo, tokens)

        # Redirect to frontend with token in query params (or use secure cookie in production)
        frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://127.0.0.1:5173"
        redirect_url = (
            f"{frontend_url}/auth/callback"
            f"?access_token={tokens.access_token}"
            f"&token_type={tokens.token_type}"
            f"&expires_in={tokens.expires_in}"
            f"&refresh_token={tokens.refresh_token or ''}"
        )
        return RedirectResponse(url=redirect_url)

    except OIDCError as e:
        frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://127.0.0.1:5173"
        redirect_url = f"{frontend_url}/auth/error?error={str(e)}"
        return RedirectResponse(url=redirect_url)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        return await auth_service.oidc_client.refresh_access_token(request.refresh_token)
    except OIDCError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserRead)
async def get_current_user(
    user_id: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Get current user by ID (for frontend to validate session)."""
    from sqlalchemy import select

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserRead.model_validate(user)


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Logout user.

    Returns Keycloak logout URL for frontend to redirect to.
    """
    logout_url = auth_service.build_logout_url(
        id_token_hint=request.id_token_hint,
        post_logout_redirect_uri=request.post_logout_redirect_uri,
    )
    return {"logout_url": logout_url}


@router.get("/logout/keycloak")
async def keycloak_logout(
    id_token_hint: Optional[str] = Query(None),
    post_logout_redirect_uri: Optional[str] = Query(None),
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """
    Redirect to Keycloak logout endpoint.

    Clears Keycloak session and redirects back to frontend.
    """
    logout_url = auth_service.build_logout_url(
        id_token_hint=id_token_hint,
        post_logout_redirect_uri=post_logout_redirect_uri,
    )
    return RedirectResponse(url=logout_url)

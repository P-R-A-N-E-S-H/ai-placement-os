from typing import Any, Dict
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Session"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Create a new student or candidate account and return initial JWT tokens."""
    request_id = getattr(request.state, "request_id", None)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await AuthService.register_user(
        db=db,
        payload=payload,
        request_id=request_id,
        ip_address=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
)
async def login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email/password and receive an access token & refresh token."""
    request_id = getattr(request.state, "request_id", None)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await AuthService.login_user(
        db=db,
        payload=payload,
        request_id=request_id,
        ip_address=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate Refresh Token",
)
async def refresh(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Rotate an unexpired refresh token for a new access token and fresh refresh token."""
    request_id = getattr(request.state, "request_id", None)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await AuthService.refresh_access_token(
        db=db,
        refresh_token_str=payload.refresh_token,
        request_id=request_id,
        ip_address=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout Current Session",
)
async def logout(
    payload: RefreshTokenRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke the current refresh token session."""
    request_id = getattr(request.state, "request_id", None)
    await AuthService.logout_user(
        db=db,
        user_id=current_user.id,
        refresh_token_str=payload.refresh_token,
        request_id=request_id,
    )
    return MessageResponse(message="Successfully logged out of current session.")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout All Sessions",
)
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke all active refresh tokens for the current user."""
    request_id = getattr(request.state, "request_id", None)
    await AuthService.logout_all_sessions(
        db=db,
        user_id=current_user.id,
        request_id=request_id,
    )
    return MessageResponse(message="Successfully logged out of all active sessions.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Authenticated User Info",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the authenticated user profile."""
    return UserResponse.model_validate(current_user)

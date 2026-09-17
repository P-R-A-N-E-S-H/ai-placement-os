from typing import Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import UserRole, decode_token
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate Bearer token and return the authenticated User model."""
    if not auth_credentials or not auth_credentials.credentials:
        raise AuthenticationError("Authorization credentials were not provided")

    token = auth_credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type. Access token required.")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload missing subject identifier")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User associated with this token no longer exists")

    if not user.is_active:
        raise AuthenticationError("User account is currently deactivated")

    return user


async def get_optional_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency that returns User or None without error."""
    if not auth_credentials or not auth_credentials.credentials:
        return None
    try:
        token = auth_credentials.credentials
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying the user is fully active."""
    return current_user


def require_role(allowed_roles: List[str]) -> Callable:
    """Dependency factory ensuring current user has one of the required roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError(
                f"Access denied: Requires role '{', '.join(allowed_roles)}', but current role is '{current_user.role}'"
            )
        return current_user

    return role_checker


def verify_resource_ownership(owner_id: str, current_user: User) -> None:
    """Ensure resource belongs to the current user, or user has administrator privileges."""
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.id != owner_id:
        raise PermissionDeniedError("You do not have permission to access or modify this resource")

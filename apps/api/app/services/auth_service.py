from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, AuthenticationError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.audit import AuditLog
from app.models.profile import UserProfile
from app.models.user import RefreshToken, User
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Core Authentication service managing registration, login, token rotation, and session security."""

    @staticmethod
    async def register_user(
        db: AsyncSession,
        payload: UserRegisterRequest,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        email = payload.email.strip().lower()

        # Check existing user
        existing_result = await db.execute(select(User).where(User.email == email))
        if existing_result.scalar_one_or_none():
            raise ValidationError(
                message="An account with this email address already exists",
                details={"field": "email"},
            )

        # Create user
        hashed_password = get_password_hash(payload.password)
        user = User(
            email=email,
            password_hash=hashed_password,
            role=payload.role or "student",
            is_active=True,
            is_verified=False,
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.flush()

        # Create associated career digital twin profile
        profile = UserProfile(
            user_id=user.id,
            full_name=payload.full_name.strip(),
            profile_completion=15.0,  # 15% for initial account creation
        )
        db.add(profile)

        # Generate tokens
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str, jti, expiry = create_refresh_token(subject=user.id)

        # Store refresh token record
        rt_record = RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_token(refresh_token_str),
            expires_at=expiry,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(rt_record)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="USER_REGISTERED",
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json={"email": email, "role": user.role},
        )
        db.add(audit)
        await db.commit()
        await db.refresh(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login_user(
        db: AsyncSession,
        payload: UserLoginRequest,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        email = payload.email.strip().lower()

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is currently deactivated")

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)

        # Generate tokens
        access_token = create_access_token(subject=user.id, role=user.role)
        refresh_token_str, jti, expiry = create_refresh_token(subject=user.id)

        # Store refresh token
        rt_record = RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_token(refresh_token_str),
            expires_at=expiry,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(rt_record)

        # Audit log
        audit = AuditLog(
            user_id=user.id,
            action="USER_LOGGED_IN",
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit)
        await db.commit()
        await db.refresh(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token_str: str,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type. Refresh token expected.")

        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise AuthenticationError("Malformed refresh token payload")

        # Lookup token record
        result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise AuthenticationError("Refresh token not found or already invalidated")

        # Reuse detection: if already revoked, compromise detected -> invalidate all user tokens
        if token_record.is_revoked:
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
            )
            audit = AuditLog(
                user_id=user_id,
                action="TOKEN_REUSE_SECURITY_ALERT",
                request_id=request_id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata_json={"compromised_jti": jti},
            )
            db.add(audit)
            await db.commit()
            raise AuthenticationError("Security violation: Revoked token reuse detected. All sessions invalidated.")

        # Check expiry
        now_utc = datetime.now(timezone.utc)
        expires_at = token_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now_utc:
            token_record.is_revoked = True
            token_record.revoked_at = now_utc
            await db.commit()
            raise AuthenticationError("Refresh token has expired. Please log in again.")

        # Fetch user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user or not user.is_active:
            raise AuthenticationError("User is no longer active")

        # Token Rotation: Revoke current token and generate replacement
        new_access_token = create_access_token(subject=user.id, role=user.role)
        new_refresh_token_str, new_jti, new_expiry = create_refresh_token(subject=user.id)

        token_record.is_revoked = True
        token_record.revoked_at = now_utc
        token_record.replaced_by_jti = new_jti

        new_token_record = RefreshToken(
            user_id=user.id,
            jti=new_jti,
            token_hash=hash_token(new_refresh_token_str),
            expires_at=new_expiry,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(new_token_record)

        audit = AuditLog(
            user_id=user.id,
            action="TOKEN_REFRESHED",
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit)
        await db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def logout_user(
        db: AsyncSession,
        user_id: str,
        refresh_token_str: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        if refresh_token_str:
            try:
                payload = decode_token(refresh_token_str)
                jti = payload.get("jti")
                if jti:
                    await db.execute(
                        update(RefreshToken)
                        .where(RefreshToken.jti == jti)
                        .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
                    )
            except Exception:
                pass

        audit = AuditLog(
            user_id=user_id,
            action="USER_LOGGED_OUT",
            request_id=request_id,
        )
        db.add(audit)
        await db.commit()

    @staticmethod
    async def logout_all_sessions(
        db: AsyncSession,
        user_id: str,
        request_id: Optional[str] = None,
    ) -> None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
        )
        audit = AuditLog(
            user_id=user_id,
            action="USER_LOGGED_OUT_ALL_SESSIONS",
            request_id=request_id,
        )
        db.add(audit)
        await db.commit()

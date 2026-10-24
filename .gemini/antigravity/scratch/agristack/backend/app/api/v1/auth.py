import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.config import settings
from ...core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    generate_totp_secret,
    verify_totp,
)
from ...core.dependencies import get_current_user
from ...core.exceptions import AuthenticationError, DuplicateResourceError, AppException
from ...models.user import User, RefreshToken, UserRole
from ...schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    MFASetupResponse,
    MFAVerifyRequest,
)
from ...services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication & MFA"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Registers a new user (Farmer, Investor, or Admin) and returns access/refresh tokens."""
    # Check duplicate email
    if db.query(User).filter(User.email == req.email.lower()).first():
        raise DuplicateResourceError(f"Email '{req.email}' is already registered")
        
    # Check duplicate phone
    if db.query(User).filter(User.phone_number == req.phone_number).first():
        raise DuplicateResourceError(f"Phone number '{req.phone_number}' is already registered")
        
    # Create user
    user = User(
        email=req.email.lower(),
        phone_number=req.phone_number,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        primary_role=req.primary_role.upper(),
        preferred_language=req.preferred_language
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Issue tokens
    access_token = create_access_token(subject=str(user.id), role=user.primary_role)
    raw_refresh, token_hash, expires_at = create_refresh_token(subject=str(user.id))
    
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(refresh_record)
    db.commit()

    AuditService.log_action(
        db=db,
        action="USER_REGISTRATION",
        resource_type="USER",
        resource_id=str(user.id),
        actor_role=user.primary_role,
        actor_id=user.id,
        ip_address=request.client.host if request.client else "127.0.0.1",
        user_agent=request.headers.get("user-agent", "Unknown"),
        details={"email": user.email, "role": user.primary_role}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        primary_role=user.primary_role,
        full_name=user.full_name,
        mfa_required=False
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticates via email/phone and password, supporting MFA OTP if enabled."""
    identifier = req.email_or_phone.strip().lower()
    user = (
        db.query(User)
        .filter((User.email == identifier) | (User.phone_number == req.email_or_phone.strip()))
        .first()
    )

    if not user or not verify_password(req.password, user.hashed_password):
        raise AuthenticationError("Invalid login credentials")

    if not user.is_active:
        raise AuthenticationError("Account is deactivated")

    # If MFA is enabled on user account
    if user.mfa_enabled:
        if not req.mfa_otp:
            # Require OTP step
            return TokenResponse(
                access_token="",
                refresh_token="",
                expires_in_seconds=0,
                user_id=str(user.id),
                primary_role=user.primary_role,
                full_name=user.full_name,
                mfa_required=True
            )
        # Verify provided OTP
        if not verify_totp(user.mfa_secret, req.mfa_otp):
            raise AuthenticationError("Invalid or expired MFA code")

    access_token = create_access_token(subject=str(user.id), role=user.primary_role)
    raw_refresh, token_hash, expires_at = create_refresh_token(subject=str(user.id))

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(refresh_record)
    db.commit()

    AuditService.log_action(
        db=db,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=str(user.id),
        actor_role=user.primary_role,
        actor_id=user.id,
        ip_address=request.client.host if request.client else "127.0.0.1",
        user_agent=request.headers.get("user-agent", "Unknown"),
        details={"mfa_used": user.mfa_enabled}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        primary_role=user.primary_role,
        full_name=user.full_name,
        mfa_required=False
    )

@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generates a new TOTP secret for the authenticated user."""
    secret = generate_totp_secret()
    current_user.mfa_secret = secret
    db.commit()

    otpauth_uri = f"otpauth://totp/AgriStack:{current_user.email}?secret={secret}&issuer=AgriStack"
    return MFASetupResponse(
        secret=secret,
        otpauth_uri=otpauth_uri,
        qr_hint=f"Scan this key into Google Authenticator or enter secret: {secret}"
    )

@router.post("/mfa/verify")
def verify_and_enable_mfa(req: MFAVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verifies a 6-digit TOTP code and activates MFA on the user account."""
    if not current_user.mfa_secret:
        raise AppException("MFA secret not initialized. Please call /mfa/setup first.")

    if not verify_totp(current_user.mfa_secret, req.code):
        raise AuthenticationError("Invalid verification code")

    current_user.mfa_enabled = True
    db.commit()
    return {"success": True, "message": "Multi-Factor Authentication enabled successfully"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Rotates refresh token and issues a new access token."""
    token_hash = hash_refresh_token(req.refresh_token)
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )

    now = datetime.now(timezone.utc)
    # Check if timezone is naive in DB datetime
    expires_at = token_record.expires_at if token_record else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if not token_record or token_record.is_revoked or (expires_at and expires_at < now):
        raise AuthenticationError("Invalid or expired refresh token")

    # Revoke old refresh token (token rotation security pattern)
    token_record.is_revoked = True

    user = token_record.user
    access_token = create_access_token(subject=str(user.id), role=user.primary_role)
    new_raw_refresh, new_hash, new_expires = create_refresh_token(subject=str(user.id))

    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        expires_at=new_expires
    )
    db.add(new_token_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw_refresh,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        primary_role=user.primary_role,
        full_name=user.full_name,
        mfa_required=False
    )

@router.post("/logout")
def logout(req: RefreshTokenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revokes the active refresh token."""
    token_hash = hash_refresh_token(req.refresh_token)
    token_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if token_record:
        token_record.is_revoked = True
        db.commit()
    return {"success": True, "message": "Logged out successfully"}

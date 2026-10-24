from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., description="Phone in E.164 format, e.g. +919876543210")
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    primary_role: str = Field(default="FARMER", description="FARMER, INVESTOR, ADMIN, GOV_OFFICER")
    preferred_language: str = Field(default="en", description="en, hi, mr")

class UserLoginRequest(BaseModel):
    email_or_phone: str
    password: str
    mfa_otp: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: str
    primary_role: str
    full_name: str
    mfa_required: bool = False

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class MFASetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    qr_hint: str

class MFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)

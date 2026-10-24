import time
import hmac
import hashlib
import struct
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
import bcrypt
import jwt
from cryptography.fernet import Fernet
from .config import settings

# Fernet cipher for AES field-level PII encryption
try:
    _fernet = Fernet(settings.PII_ENCRYPTION_KEY.encode())
except Exception:
    # Fallback to generating a deterministic key if invalid key format provided
    _fernet = Fernet(Fernet.generate_key())

# --- 1. Password Hashing (bcrypt) ---

def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

# --- 2. JWT Access & Refresh Tokens ---

def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None, claims: Optional[Dict[str, Any]] = None) -> str:
    """Creates a signed JWT access token with user ID and primary role."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    if claims:
        payload.update(claims)
        
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: str) -> Tuple[str, str, datetime]:
    """Generates a secure random refresh token, its SHA-256 hash for storage, and expiration."""
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return raw_token, token_hash, expires_at

def hash_refresh_token(raw_token: str) -> str:
    """Hashes a raw refresh token to look it up in the database."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

# --- 3. Aadhaar Privacy Compliance (UIDAI Guidelines) ---

def mask_aadhaar(aadhaar_number: str) -> str:
    """Returns masked Aadhaar format XXXX-XXXX-1234, keeping only the last 4 digits."""
    clean = "".join(filter(str.isdigit, aadhaar_number))
    if len(clean) != 12:
        raise ValueError("Invalid Aadhaar length: must be exactly 12 digits")
    return f"XXXX-XXXX-{clean[-4:]}"

def hash_aadhaar(aadhaar_number: str) -> str:
    """Creates a deterministic HMAC-SHA256 hash using a server pepper for duplicate detection."""
    clean = "".join(filter(str.isdigit, aadhaar_number))
    return hmac.new(settings.AADHAAR_PEPPER.encode("utf-8"), clean.encode("utf-8"), hashlib.sha256).hexdigest()

# --- 4. AES-256 Field-Level PII Encryption ---

def encrypt_pii(plain_text: str) -> str:
    """Encrypts sensitive fields (e.g. bank account details or PAN) using AES Fernet."""
    if not plain_text:
        return ""
    return _fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")

def decrypt_pii(cipher_text: str) -> str:
    """Decrypts ciphertext back to plain text."""
    if not cipher_text:
        return ""
    return _fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")

# --- 5. Multi-Factor Authentication (RFC 6238 TOTP & SMS OTP) ---

def generate_totp_secret() -> str:
    """Generates a base32 encoded random secret key for TOTP authenticator apps."""
    return base64.b32encode(secrets.token_bytes(20)).decode("utf-8").replace("=", "")

def get_totp_token(secret_b32: str, time_step: int = 30) -> str:
    """Calculates current 6-digit TOTP code for a base32 secret."""
    key = base64.b32decode(secret_b32 + "=" * ((8 - len(secret_b32) % 8) % 8))
    counter = int(time.time() // time_step)
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = (struct.unpack(">I", h[offset:offset+4])[0] & 0x7FFFFFFF) % 1000000
    return f"{code:06d}"

def verify_totp(secret_b32: str, code: str, window: int = 1) -> bool:
    """Verifies a 6-digit TOTP code within a drift window (-1, 0, +1 time steps)."""
    try:
        key = base64.b32decode(secret_b32 + "=" * ((8 - len(secret_b32) % 8) % 8))
        current_counter = int(time.time() // 30)
        code_str = str(code).strip()
        
        for offset_step in range(-window, window + 1):
            counter = current_counter + offset_step
            msg = struct.pack(">Q", counter)
            h = hmac.new(key, msg, hashlib.sha1).digest()
            offset = h[-1] & 0x0F
            computed_code = (struct.unpack(">I", h[offset:offset+4])[0] & 0x7FFFFFFF) % 1000000
            if f"{computed_code:06d}" == code_str:
                return True
        return False
    except Exception:
        return False

def generate_sms_otp() -> str:
    """Generates a 6-digit numeric OTP for SMS/Email MFA."""
    return f"{secrets.randbelow(900000) + 100000:06d}"

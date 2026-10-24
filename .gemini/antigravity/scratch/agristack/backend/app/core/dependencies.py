from typing import List, Callable
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .security import decode_access_token
from .exceptions import AuthenticationError, PermissionDeniedError
from ..models.user import User, UserRole

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to extract and validate the authenticated user from JWT Bearer token."""
    if not credentials:
        raise AuthenticationError("Authorization header missing or invalid", details={"scheme": "Bearer"})
    
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise AuthenticationError(f"Invalid or expired access token: {str(e)}")
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token payload missing subject identifier")
    
    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID format in token")
        
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise AuthenticationError("User associated with token does not exist")
    
    if not user.is_active:
        raise PermissionDeniedError("Account is inactive or deactivated")
        
    return user

def require_roles(allowed_roles: List[str]) -> Callable:
    """Dependency factory that enforces Role-Based Access Control (RBAC)."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.primary_role not in allowed_roles:
            raise PermissionDeniedError(
                f"Role '{current_user.primary_role}' is not authorized to access this endpoint. "
                f"Required one of: {allowed_roles}"
            )
        return current_user
    return role_checker

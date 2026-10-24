from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base application exception with error code and status."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

class EntityNotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND, details=details)

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, code="UNAUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED, details=details)

class PermissionDeniedError(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action", details: Optional[Any] = None):
        super().__init__(message, code="FORBIDDEN", status_code=status.HTTP_403_FORBIDDEN, details=details)

class InvalidStateTransitionError(AppException):
    def __init__(self, message: str = "Invalid project state machine transition", details: Optional[Any] = None):
        super().__init__(message, code="INVALID_STATE_TRANSITION", status_code=422, details=details)

class LedgerIntegrityError(AppException):
    def __init__(self, message: str = "Ownership ledger cryptographic integrity check failed", details: Optional[Any] = None):
        super().__init__(message, code="LEDGER_TAMPER_DETECTED", status_code=status.HTTP_409_CONFLICT, details=details)

class DuplicateResourceError(AppException):
    def __init__(self, message: str = "Resource already exists", details: Optional[Any] = None):
        super().__init__(message, code="DUPLICATE_RESOURCE", status_code=status.HTTP_409_CONFLICT, details=details)

class PaymentVerificationError(AppException):
    def __init__(self, message: str = "Payment verification failed or signature mismatch", details: Optional[Any] = None):
        super().__init__(message, code="PAYMENT_VERIFICATION_FAILED", status_code=status.HTTP_400_BAD_REQUEST, details=details)

# Convenient aliases
NotFoundError = EntityNotFoundError
ForbiddenError = PermissionDeniedError
ValidationError = AppException

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Standardized JSON error handler for all application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            }
        }
    )

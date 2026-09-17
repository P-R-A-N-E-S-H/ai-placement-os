import uuid
from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    request_id: str


class StandardResponse(BaseModel):
    success: bool = False
    error: ErrorResponse


class AppException(Exception):
    """Base application exception with HTTP status mapping and machine-readable error codes."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class EntityNotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AgentExecutionError(AppException):
    def __init__(self, message: str = "Agent execution failure", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


class PromptInjectionDetectedError(AppException):
    def __init__(self, message: str = "Security policy violation detected in input", details: Optional[Any] = None):
        super().__init__(
            message=message,
            code="PROMPT_INJECTION_DETECTED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": str(exc) if request.app.debug else None,
                "request_id": request_id,
            },
        },
    )

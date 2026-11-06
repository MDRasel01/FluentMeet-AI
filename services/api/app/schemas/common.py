from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[List[Any]] = None

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    message: Optional[str] = None
    request_id: Optional[str] = None

    @classmethod
    def ok_response(cls, data: Optional[T] = None, message: Optional[str] = None) -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def error_response(cls, message: str, code: str = "ERROR", details: Optional[List[Any]] = None) -> "ApiResponse[None]":
        return cls(
            success=False,
            error=ErrorDetail(code=code, message=message, details=details),
            message=message
        )

"""Common API response schemas for unified responses."""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Unified API response wrapper.
    
    All API responses follow this structure:
    {
        "success": true,
        "data": <response data>,
        "message": "optional message"
    }
    """
    success: bool = Field(True, description="Indicates if the request was successful")
    data: T = Field(description="Response data payload")
    message: Optional[str] = Field(None, description="Optional message for the response")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records per page")
    total: int = Field(description="Total number of records available")


class PaginatedResponse(BaseModel, Generic[T]):
    """Unified paginated response wrapper.
    
    For list endpoints with pagination:
    {
        "success": true,
        "data": [<items>],
        "pagination": {
            "skip": 0,
            "limit": 100,
            "total": 1000
        },
        "message": "optional message"
    }
    """
    success: bool = Field(True, description="Indicates if the request was successful")
    data: list[T] = Field(description="List of items")
    pagination: PaginationMeta = Field(description="Pagination metadata")
    message: Optional[str] = Field(None, description="Optional message for the response")


class ErrorResponse(BaseModel):
    """Standardized error response format."""
    success: bool = Field(False, description="Indicates the request failed")
    error: dict = Field(description="Error information")


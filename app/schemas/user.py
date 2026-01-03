"""User Pydantic schemas for API validation."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import zoneinfo


class UserBase(BaseModel):
    """Base schema with common user fields."""
    email: EmailStr
    first_name: str
    last_name: str
    timezone: str
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate that timezone is a valid IANA timezone name."""
        try:
            zoneinfo.ZoneInfo(v)
            return v
        except Exception:
            raise ValueError(f"Invalid timezone: {v}. Must be a valid IANA timezone (e.g., 'America/New_York', 'UTC')")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserResponse(UserBase):
    """Schema for user response (includes all fields except deleted_at)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


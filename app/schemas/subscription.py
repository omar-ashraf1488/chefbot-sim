"""Subscription Pydantic schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class SubscriptionBase(BaseModel):
    """Base schema with common subscription fields."""
    user_id: UUID
    status: str  # Active, Paused, Cancelled
    preferences: Optional[dict[str, bool | str]] = None  # JSON object: {"No Fish": true, "Vegan": true}
    started_at: datetime
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"Active", "Paused", "Cancelled"}
        if v not in allowed_statuses:
            raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate that preferences is a dict if provided."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("Preferences must be a dictionary/JSON object")
        return v


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new subscription."""
    pass


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription (all fields optional)."""
    status: str | None = None
    preferences: Optional[dict[str, bool | str]] = None
    started_at: datetime | None = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate that status is one of the allowed values if provided."""
        if v is not None:
            allowed_statuses = {"Active", "Paused", "Cancelled"}
            if v not in allowed_statuses:
                raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate that preferences is a dict if provided."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("Preferences must be a dictionary/JSON object")
        return v


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response (includes all fields except deleted_at)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


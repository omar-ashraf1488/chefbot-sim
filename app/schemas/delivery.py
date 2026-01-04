"""Delivery Pydantic schemas for API validation."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class DeliveryBase(BaseModel):
    """Base schema with common delivery fields."""
    order_id: UUID
    status: str  # delivered, delayed, failed, in_transit
    expected_delivery_date: datetime  # When the box should arrive
    actual_delivery_date: Optional[datetime] = None  # When the box actually arrived
    tracking_number: Optional[str] = None  # Shipping tracking number
    notes: Optional[str] = None  # Additional delivery notes
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"delivered", "delayed", "failed", "in_transit"}
        if v not in allowed_statuses:
            raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v


class DeliveryCreate(DeliveryBase):
    """Schema for creating a new delivery."""
    pass


class DeliveryResponse(DeliveryBase):
    """Schema for delivery response (includes all fields except deleted_at)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


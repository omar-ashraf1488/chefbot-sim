"""Order Pydantic schemas for API validation."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class OrderBase(BaseModel):
    """Base schema with common order fields."""
    subscription_id: UUID
    recipes: list[dict]  # JSON list: [{"id": "uuid", "name": "Recipe Name"}, ...]
    total_amount: Decimal  # Total price for this order
    status: str  # pending, shipped, delivered, cancelled
    order_date: datetime  # When the order was placed
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"pending", "shipped", "delivered", "cancelled"}
        if v not in allowed_statuses:
            raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: Decimal) -> Decimal:
        """Validate that total_amount is positive."""
        if v < 0:
            raise ValueError("Total amount must be a positive number")
        return v
    
    @field_validator('recipes')
    @classmethod
    def validate_recipes(cls, v: list[dict]) -> list[dict]:
        """Validate that recipes is a non-empty list of dictionaries."""
        if not isinstance(v, list):
            raise ValueError("Recipes must be a list")
        if len(v) == 0:
            raise ValueError("Recipes list cannot be empty")
        if not all(isinstance(recipe, dict) for recipe in v):
            raise ValueError("All recipes must be dictionaries")
        return v


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an order (limited fields, primarily status)."""
    status: str | None = None
    total_amount: Decimal | None = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate that status is one of the allowed values if provided."""
        if v is not None:
            allowed_statuses = {"pending", "shipped", "delivered", "cancelled"}
            if v not in allowed_statuses:
                raise ValueError(f"Invalid status: {v}. Must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: Decimal | None) -> Decimal | None:
        """Validate that total_amount is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Total amount must be a positive number")
        return v


class OrderResponse(OrderBase):
    """Schema for order response (includes all fields except deleted_at)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


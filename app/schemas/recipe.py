"""Recipe Pydantic schemas for API validation."""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class RecipeBase(BaseModel):
    """Base schema with common recipe fields."""
    name: str
    description: Optional[str] = None
    calories: int  # Calories per serving
    tags: Optional[list[str]] = None  # JSON array: ["Keto", "Family-Friendly", "Vegetarian"]
    price: Optional[Decimal] = None  # Price in currency (e.g., 24.99)
    preparation_time: Optional[int] = None  # Preparation time in minutes
    servings: Optional[int] = None  # Number of servings
    image_url: Optional[str] = None  # URL to recipe image
    
    @field_validator('calories')
    @classmethod
    def validate_calories(cls, v: int) -> int:
        """Validate that calories is a positive number."""
        if v < 0:
            raise ValueError("Calories must be a positive number")
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that price is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Price must be a positive number")
        return v
    
    @field_validator('preparation_time', 'servings')
    @classmethod
    def validate_positive_integers(cls, v: Optional[int]) -> Optional[int]:
        """Validate that preparation_time and servings are positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Must be a positive number")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate that tags is a list of strings if provided."""
        if v is not None and not isinstance(v, list):
            raise ValueError("Tags must be a list of strings")
        if v is not None and not all(isinstance(tag, str) for tag in v):
            raise ValueError("All tags must be strings")
        return v


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe (all fields optional)."""
    name: str | None = None
    description: str | None = None
    calories: int | None = None
    tags: list[str] | None = None
    price: Optional[Decimal] = None
    preparation_time: int | None = None
    servings: int | None = None
    image_url: str | None = None
    
    @field_validator('calories')
    @classmethod
    def validate_calories(cls, v: int | None) -> int | None:
        """Validate that calories is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Calories must be a positive number")
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that price is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Price must be a positive number")
        return v
    
    @field_validator('preparation_time', 'servings')
    @classmethod
    def validate_positive_integers(cls, v: int | None) -> int | None:
        """Validate that preparation_time and servings are positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Must be a positive number")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate that tags is a list of strings if provided."""
        if v is not None and not isinstance(v, list):
            raise ValueError("Tags must be a list of strings")
        if v is not None and not all(isinstance(tag, str) for tag in v):
            raise ValueError("All tags must be strings")
        return v


class RecipeResponse(RecipeBase):
    """Schema for recipe response (includes all fields except deleted_at)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


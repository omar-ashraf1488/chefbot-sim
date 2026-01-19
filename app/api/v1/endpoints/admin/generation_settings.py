"""Admin generation settings API endpoints."""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.schemas import Response
from app.core.tasks.delivery_generation import (
    get_delivery_generation_settings,
    update_delivery_generation_settings
)
from app.core.tasks.order_generation import (
    get_order_generation_settings,
    update_order_generation_settings
)
from app.core.tasks.recipe_generation import (
    get_recipe_generation_settings,
    update_recipe_generation_settings
)
from app.core.tasks.subscription_generation import (
    get_subscription_generation_settings,
    update_subscription_generation_settings
)
from app.core.tasks.user_generation import (
    get_user_generation_settings,
    update_user_generation_settings
)

router = APIRouter()


class UserGenerationSettings(BaseModel):
    """User generation settings."""
    male_weight: Optional[float] = Field(
        None,
        description="Weight for Male gender (0.0 to 1.0). Female weight is automatically 1.0 - male_weight",
        ge=0.0,
        le=1.0
    )
    interval: Optional[int] = Field(None, description="Generation interval in seconds", ge=1)


class RecipeGenerationSettings(BaseModel):
    """Recipe generation settings."""
    interval: Optional[int] = Field(None, description="Generation interval in seconds", ge=1)


class SubscriptionGenerationSettings(BaseModel):
    """Subscription generation settings."""
    status_weights: Optional[list[float]] = Field(
        None,
        description="Weights for [Active, Paused, Cancelled] statuses. Must sum to 1.0",
        min_length=3,
        max_length=3
    )
    interval: Optional[int] = Field(None, description="Generation interval in seconds", ge=1)


class OrderGenerationSettings(BaseModel):
    """Order generation settings."""
    status_weights: Optional[list[float]] = Field(
        None,
        description="Weights for [pending, shipped, delivered, cancelled] statuses. Must sum to 1.0",
        min_length=4,
        max_length=4
    )
    interval: Optional[int] = Field(None, description="Generation interval in seconds", ge=1)


class DeliveryGenerationSettings(BaseModel):
    """Delivery generation settings."""
    status_weights: Optional[list[float]] = Field(
        None,
        description="Weights for [delivered, delayed, failed, in_transit] statuses. Must sum to 1.0",
        min_length=4,
        max_length=4
    )
    interval: Optional[int] = Field(None, description="Generation interval in seconds", ge=1)


class AllGenerationSettings(BaseModel):
    """All generation settings."""
    user: Optional[UserGenerationSettings] = None
    recipe: Optional[RecipeGenerationSettings] = None
    subscription: Optional[SubscriptionGenerationSettings] = None
    order: Optional[OrderGenerationSettings] = None
    delivery: Optional[DeliveryGenerationSettings] = None


class AllGenerationSettingsResponse(BaseModel):
    """Response model for all generation settings."""
    user: dict
    recipe: dict
    subscription: dict
    order: dict
    delivery: dict


@router.get("/generation/settings", response_model=Response[AllGenerationSettingsResponse], status_code=200)
def get_all_generation_settings():
    """Get all generation settings.
    
    Admin-only endpoint. Returns current settings for all generation tasks.
    Note: In production, this would require admin authentication/authorization.
    """
    return Response(
        success=True,
        data=AllGenerationSettingsResponse(
            user=get_user_generation_settings(),
            recipe=get_recipe_generation_settings(),
            subscription=get_subscription_generation_settings(),
            order=get_order_generation_settings(),
            delivery=get_delivery_generation_settings()
        )
    )


@router.put("/generation/settings", response_model=Response[AllGenerationSettingsResponse], status_code=200)
def update_all_generation_settings(settings: AllGenerationSettings):
    """Update generation settings for all tasks.
    
    Admin-only endpoint. Updates settings for any generation task.
    Only fields present in the request body will be updated; others remain unchanged.
    Note: In production, this would require admin authentication/authorization.
    
    Example:
    {
        "user": {"interval": 30},
        "subscription": {"status_weights": [0.80, 0.10, 0.10], "interval": 20},
        "order": {"interval": 15}
    }
    """
    errors = []
    
    # Update user generation settings
    if settings.user:
        try:
            update_user_generation_settings(
                male_weight=settings.user.male_weight,
                interval=settings.user.interval
            )
        except ValueError as e:
            errors.append(f"User generation: {str(e)}")
    
    # Update recipe generation settings
    if settings.recipe:
        try:
            update_recipe_generation_settings(interval=settings.recipe.interval)
        except ValueError as e:
            errors.append(f"Recipe generation: {str(e)}")
    
    # Update subscription generation settings
    if settings.subscription:
        try:
            update_subscription_generation_settings(
                status_weights=settings.subscription.status_weights,
                interval=settings.subscription.interval
            )
        except ValueError as e:
            errors.append(f"Subscription generation: {str(e)}")
    
    # Update order generation settings
    if settings.order:
        try:
            update_order_generation_settings(
                status_weights=settings.order.status_weights,
                interval=settings.order.interval
            )
        except ValueError as e:
            errors.append(f"Order generation: {str(e)}")
    
    # Update delivery generation settings
    if settings.delivery:
        try:
            update_delivery_generation_settings(
                status_weights=settings.delivery.status_weights,
                interval=settings.delivery.interval
            )
        except ValueError as e:
            errors.append(f"Delivery generation: {str(e)}")
    
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))
    
    return Response(
        success=True,
        data=AllGenerationSettingsResponse(
            user=get_user_generation_settings(),
            recipe=get_recipe_generation_settings(),
            subscription=get_subscription_generation_settings(),
            order=get_order_generation_settings(),
            delivery=get_delivery_generation_settings()
        ),
        message="Settings updated successfully"
    )

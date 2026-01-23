"""Admin generation settings API endpoints."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

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


def get_templates(request: Request) -> Jinja2Templates:
    """Get Jinja2 templates from app state."""
    return request.app.state.templates


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


@router.get("/generation/settings/form", response_class=HTMLResponse)
def get_generation_settings_form(request: Request):
    """Render the generation settings form template.
    
    Admin-only endpoint. Returns an HTML form for configuring generation settings.
    Note: In production, this would require admin authentication/authorization.
    """
    templates = get_templates(request)
    
    # Get current settings
    current_settings = AllGenerationSettingsResponse(
        user=get_user_generation_settings(),
        recipe=get_recipe_generation_settings(),
        subscription=get_subscription_generation_settings(),
        order=get_order_generation_settings(),
        delivery=get_delivery_generation_settings()
    )
    
    # Convert to a format suitable for the template
    settings_dict = {
        "user": {
            "male_weight": current_settings.user.get("male_weight"),
            "interval": current_settings.user.get("interval")
        },
        "recipe": {
            "interval": current_settings.recipe.get("interval")
        },
        "subscription": {
            "status_weights": current_settings.subscription.get("status_weights"),
            "interval": current_settings.subscription.get("interval")
        },
        "order": {
            "status_weights": current_settings.order.get("status_weights"),
            "interval": current_settings.order.get("interval")
        },
        "delivery": {
            "status_weights": current_settings.delivery.get("status_weights"),
            "interval": current_settings.delivery.get("interval")
        }
    }
    
    return templates.TemplateResponse(
        "generation_settings.html",
        {"request": request, "settings": settings_dict}
    )


@router.post("/generation/settings/form", response_class=HTMLResponse)
async def update_generation_settings_form(request: Request):
    """Handle form submission for generation settings.
    
    Admin-only endpoint. Processes form data and updates generation settings.
    Note: In production, this would require admin authentication/authorization.
    """
    templates = get_templates(request)
    
    # Parse form data
    form_data = await request.form()
    
    # Helper function to parse optional float
    def parse_float(value: str | None) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Helper function to parse optional int
    def parse_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    # Helper function to parse list of floats
    def parse_float_list(values: list[str] | str | None) -> list[float] | None:
        if values is None:
            return None
        if isinstance(values, str):
            values = [values]
        try:
            parsed = [float(v) for v in values if v and v.strip()]
            return parsed if parsed else None
        except (ValueError, TypeError):
            return None
    
    # Extract form values
    user_male_weight = parse_float(form_data.get("user_male_weight"))
    user_interval = parse_int(form_data.get("user_interval"))
    recipe_interval = parse_int(form_data.get("recipe_interval"))
    subscription_status_weights = parse_float_list(form_data.getlist("subscription_status_weights"))
    subscription_interval = parse_int(form_data.get("subscription_interval"))
    order_status_weights = parse_float_list(form_data.getlist("order_status_weights"))
    order_interval = parse_int(form_data.get("order_interval"))
    delivery_status_weights = parse_float_list(form_data.getlist("delivery_status_weights"))
    delivery_interval = parse_int(form_data.get("delivery_interval"))
    
    # Build settings object from form data
    settings = AllGenerationSettings()
    
    if user_male_weight is not None or user_interval is not None:
        settings.user = UserGenerationSettings(
            male_weight=user_male_weight,
            interval=user_interval
        )
    
    if recipe_interval is not None:
        settings.recipe = RecipeGenerationSettings(interval=recipe_interval)
    
    if subscription_status_weights or subscription_interval is not None:
        settings.subscription = SubscriptionGenerationSettings(
            status_weights=subscription_status_weights,
            interval=subscription_interval
        )
    
    if order_status_weights or order_interval is not None:
        settings.order = OrderGenerationSettings(
            status_weights=order_status_weights,
            interval=order_interval
        )
    
    if delivery_status_weights or delivery_interval is not None:
        settings.delivery = DeliveryGenerationSettings(
            status_weights=delivery_status_weights,
            interval=delivery_interval
        )
    
    # Update settings
    errors = []
    
    if settings.user:
        try:
            update_user_generation_settings(
                male_weight=settings.user.male_weight,
                interval=settings.user.interval
            )
        except ValueError as e:
            errors.append(f"User generation: {str(e)}")
    
    if settings.recipe:
        try:
            update_recipe_generation_settings(interval=settings.recipe.interval)
        except ValueError as e:
            errors.append(f"Recipe generation: {str(e)}")
    
    if settings.subscription:
        try:
            update_subscription_generation_settings(
                status_weights=settings.subscription.status_weights,
                interval=settings.subscription.interval
            )
        except ValueError as e:
            errors.append(f"Subscription generation: {str(e)}")
    
    if settings.order:
        try:
            update_order_generation_settings(
                status_weights=settings.order.status_weights,
                interval=settings.order.interval
            )
        except ValueError as e:
            errors.append(f"Order generation: {str(e)}")
    
    if settings.delivery:
        try:
            update_delivery_generation_settings(
                status_weights=settings.delivery.status_weights,
                interval=settings.delivery.interval
            )
        except ValueError as e:
            errors.append(f"Delivery generation: {str(e)}")
    
    # Get updated settings for template
    current_settings = AllGenerationSettingsResponse(
        user=get_user_generation_settings(),
        recipe=get_recipe_generation_settings(),
        subscription=get_subscription_generation_settings(),
        order=get_order_generation_settings(),
        delivery=get_delivery_generation_settings()
    )
    
    settings_dict = {
        "user": {
            "male_weight": current_settings.user.get("male_weight"),
            "interval": current_settings.user.get("interval")
        },
        "recipe": {
            "interval": current_settings.recipe.get("interval")
        },
        "subscription": {
            "status_weights": current_settings.subscription.get("status_weights"),
            "interval": current_settings.subscription.get("interval")
        },
        "order": {
            "status_weights": current_settings.order.get("status_weights"),
            "interval": current_settings.order.get("interval")
        },
        "delivery": {
            "status_weights": current_settings.delivery.get("status_weights"),
            "interval": current_settings.delivery.get("interval")
        }
    }
    
    # Prepare message
    message = "Settings updated successfully" if not errors else "; ".join(errors)
    success = len(errors) == 0
    
    return templates.TemplateResponse(
        "generation_settings.html",
        {
            "request": request,
            "settings": settings_dict,
            "message": message,
            "success": success
        }
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

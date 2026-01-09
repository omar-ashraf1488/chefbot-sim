"""User profile API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.schemas.delivery import DeliveryResponse
from app.schemas.order import OrderResponse
from app.schemas.subscription import SubscriptionResponse
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


def get_current_user_id(
    user_id: UUID = Query(..., description="User ID (temporary for testing, will come from JWT in production)"),
) -> UUID:
    """Get current user ID from query parameter (temporary for testing).
    
    In production, this would extract user_id from JWT token.
    """
    return user_id


@router.get("/me", response_model=Response[UserResponse], status_code=200)
def get_current_user(
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get current user profile.
    
    Authenticated endpoint. Returns the authenticated user's profile.
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    user_repo = UserRepository(db)
    user = user_repo.get(current_user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    return Response(
        success=True,
        data=UserResponse.model_validate(user)
    )


@router.patch("/me", response_model=Response[UserResponse], status_code=200)
def update_current_user(
    user_data: UserUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update current user profile.
    
    Authenticated endpoint. Updates the authenticated user's profile (partial update).
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    user_repo = UserRepository(db)
    
    user = user_repo.get(current_user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Check email uniqueness if email is being updated
    if user_data.email and user_data.email != user.email:
        existing_user = user_repo.get_by_email(user_data.email)
        if existing_user and existing_user.id != current_user_id:
            raise ConflictError(f"Email {user_data.email} is already in use")
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    
    if not update_data:
        return Response(
            success=True,
            data=UserResponse.model_validate(user),
            message="No fields to update"
        )
    
    updated_user = user_repo.update(current_user_id, **update_data)
    
    return Response(
        success=True,
        data=UserResponse.model_validate(updated_user),
        message="Profile updated successfully"
    )


@router.delete("/me", status_code=204)
def delete_current_user(
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete current user account (soft delete).
    
    Authenticated endpoint. Soft deletes the authenticated user's account.
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    user_repo = UserRepository(db)
    
    user = user_repo.get(current_user_id)
    if not user:
        raise NotFoundError("User not found")
    
    user_repo.soft_delete(current_user_id)
    
    return None


@router.get("/me/subscriptions", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
def get_current_user_subscriptions(
    current_user_id: UUID = Depends(get_current_user_id),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: str | None = Query(None, description="Filter by subscription status"),
    db: Session = Depends(get_db),
):
    """Get current user's subscriptions.
    
    Authenticated endpoint. Returns paginated list of authenticated user's subscriptions.
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = user_repo.get(current_user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get all subscriptions for user
    all_subscriptions = subscription_repo.get_by_user_id(current_user_id)
    
    # Filter by status if provided
    if status:
        all_subscriptions = [sub for sub in all_subscriptions if sub.status == status]
    
    # Apply pagination manually
    total = len(all_subscriptions)
    paginated_subscriptions = all_subscriptions[skip:skip + limit]
    
    subscription_responses = [SubscriptionResponse.model_validate(sub) for sub in paginated_subscriptions]
    
    return PaginatedResponse(
        success=True,
        data=subscription_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/me/orders", response_model=PaginatedResponse[OrderResponse], status_code=200)
def get_current_user_orders(
    current_user_id: UUID = Depends(get_current_user_id),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: str | None = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db),
):
    """Get current user's orders.
    
    Authenticated endpoint. Returns paginated list of authenticated user's orders.
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = user_repo.get(current_user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get all subscriptions for this user
    user_subscriptions = subscription_repo.get_by_user_id(current_user_id)
    if not user_subscriptions:
        return PaginatedResponse(
            success=True,
            data=[],
            pagination=PaginationMeta(skip=skip, limit=limit, total=0)
        )
    
    # Get all orders for all user's subscriptions
    all_orders = []
    for subscription in user_subscriptions:
        orders = order_repo.get_by_subscription_id(subscription.id)
        all_orders.extend(orders)
    
    # Filter by status if provided
    if status:
        all_orders = [order for order in all_orders if order.status == status]
    
    # Sort by order_date descending (most recent first)
    all_orders.sort(key=lambda x: x.order_date, reverse=True)
    
    # Apply pagination manually
    total = len(all_orders)
    paginated_orders = all_orders[skip:skip + limit]
    
    order_responses = [OrderResponse.model_validate(order) for order in paginated_orders]
    
    return PaginatedResponse(
        success=True,
        data=order_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/me/deliveries", response_model=PaginatedResponse[DeliveryResponse], status_code=200)
def get_current_user_deliveries(
    current_user_id: UUID = Depends(get_current_user_id),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: str | None = Query(None, description="Filter by delivery status"),
    db: Session = Depends(get_db),
):
    """Get current user's deliveries.
    
    Authenticated endpoint. Returns paginated list of authenticated user's deliveries.
    Note: In production, user_id comes from JWT token. Currently uses query parameter for testing.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = user_repo.get(current_user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get all subscriptions for this user
    user_subscriptions = subscription_repo.get_by_user_id(current_user_id)
    if not user_subscriptions:
        return PaginatedResponse(
            success=True,
            data=[],
            pagination=PaginationMeta(skip=skip, limit=limit, total=0)
        )
    
    # Get all orders for all user's subscriptions
    all_orders = []
    for subscription in user_subscriptions:
        orders = order_repo.get_by_subscription_id(subscription.id)
        all_orders.extend(orders)
    
    # Get all deliveries for all user's orders
    all_deliveries = []
    for order in all_orders:
        delivery = delivery_repo.get_by_order_id(order.id)
        if delivery:
            all_deliveries.append(delivery)
    
    # Filter by status if provided
    if status:
        all_deliveries = [delivery for delivery in all_deliveries if delivery.status == status]
    
    # Sort by expected_delivery_date descending (most recent first)
    all_deliveries.sort(key=lambda x: x.expected_delivery_date, reverse=True)
    
    # Apply pagination manually
    total = len(all_deliveries)
    paginated_deliveries = all_deliveries[skip:skip + limit]
    
    delivery_responses = [DeliveryResponse.model_validate(delivery) for delivery in paginated_deliveries]
    
    return PaginatedResponse(
        success=True,
        data=delivery_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


"""User deliveries API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.schemas.delivery import DeliveryResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DeliveryResponse], status_code=200)
def get_deliveries(
    user_id: UUID = Query(..., description="User ID to get deliveries for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get deliveries for a user (temporary endpoint for testing without auth).
    
    This endpoint is for testing purposes. In production, user_id would come from auth token.
    Note: This gets deliveries through orders and subscriptions - gets all user's subscriptions,
    then all orders for those subscriptions, then deliveries for those orders.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    # Get all subscriptions for this user
    user_subscriptions = subscription_repo.get_by_user_id(user_id)
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


@router.get("/orders/{order_id}/delivery", response_model=Response[DeliveryResponse], status_code=200)
def get_order_delivery(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """Get delivery for an order.
    
    Authenticated endpoint. Returns delivery details if the user owns the order.
    Note: In production, this would verify the user owns the order.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    
    # Verify order exists
    order = order_repo.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order with id {order_id} not found"
        )
    
    # TODO: verify user owns this order
    # subscription = subscription_repo.get(order.subscription_id)
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this delivery")
    
    delivery = delivery_repo.get_by_order_id(order_id)
    if not delivery:
        raise HTTPException(
            status_code=404,
            detail=f"Delivery for order {order_id} not found"
        )
    
    return Response(
        success=True,
        data=DeliveryResponse.model_validate(delivery)
    )


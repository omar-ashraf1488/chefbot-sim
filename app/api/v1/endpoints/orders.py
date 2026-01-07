"""User orders API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderResponse], status_code=200)
def get_orders(
    user_id: UUID = Query(..., description="User ID to get orders for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get orders for a user (temporary endpoint for testing without auth).
    
    This endpoint is for testing purposes. In production, users would use /me/orders
    which gets the user_id from the authentication token.
    Note: This gets orders through subscriptions - gets all user's subscriptions first.
    """
    from app.core.repositories.user_repository import UserRepository
    
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


@router.post("", response_model=Response[OrderResponse], status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    """Create an order for current user's subscription.
    
    Authenticated endpoint. Creates an order for the authenticated user's subscription.
    Note: In production, this would verify the subscription belongs to the authenticated user.
    """
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    
    # Verify subscription exists
    subscription = subscription_repo.get(order_data.subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {order_data.subscription_id} not found"
        )
    
    # TODO: verify subscription belongs to authenticated user
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to create order for this subscription")
    
    order = order_repo.create(**order_data.model_dump())
    
    return Response(
        success=True,
        data=OrderResponse.model_validate(order),
        message="Order created successfully"
    )


@router.get("/{order_id}", response_model=Response[OrderResponse], status_code=200)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """Get an order by ID.
    
    Authenticated endpoint. Returns order details if the user owns it (via subscription).
    Note: In production, this would verify the user owns the order.
    """
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    
    order = order_repo.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order with id {order_id} not found"
        )
    
    # TODO: verify user owns this order
    # subscription = subscription_repo.get(order.subscription_id)
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
    return Response(
        success=True,
        data=OrderResponse.model_validate(order)
    )


@router.get("/subscriptions/{subscription_id}/orders", response_model=PaginatedResponse[OrderResponse], status_code=200)
def get_subscription_orders(
    subscription_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get orders for a subscription.
    
    Authenticated endpoint. Returns orders for a subscription if the user owns it.
    Note: In production, this would verify the subscription belongs to the authenticated user.
    """
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    
    # Verify subscription exists
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # TODO: verify subscription belongs to authenticated user
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this subscription's orders")
    
    orders = order_repo.get_by_subscription_id(subscription_id, skip=skip, limit=limit)
    total = order_repo.count_by_subscription_id(subscription_id)
    
    order_responses = [OrderResponse.model_validate(order) for order in orders]
    
    return PaginatedResponse(
        success=True,
        data=order_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


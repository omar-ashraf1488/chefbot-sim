"""Admin orders API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderResponse], status_code=200)
def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    subscription_id: UUID | None = Query(None, description="Filter by subscription ID"),
    status: str | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all orders with optional filtering.
    
    Admin-only endpoint. Returns paginated list of all orders.
    Note: In production, this would require admin authentication/authorization.
    """
    order_repo = OrderRepository(db)
    
    # Build filters
    filters = {}
    if subscription_id:
        # Verify subscription exists
        subscription_repo = SubscriptionRepository(db)
        subscription = subscription_repo.get(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail=f"Subscription with id {subscription_id} not found")
        filters["subscription_id"] = subscription_id
    if status:
        filters["status"] = status
    
    orders = order_repo.get_all(skip=skip, limit=limit, **filters)
    total = order_repo.count(**filters)
    
    order_responses = [OrderResponse.model_validate(order) for order in orders]
    
    return PaginatedResponse(
        success=True,
        data=order_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/{order_id}", response_model=Response[OrderResponse], status_code=200)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """Get an order by ID.
    
    Admin-only endpoint. Returns order details by ID.
    Note: In production, this would require admin authentication/authorization.
    """
    order_repo = OrderRepository(db)
    order = order_repo.get(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    
    return Response(
        success=True,
        data=OrderResponse.model_validate(order)
    )


@router.post("", response_model=Response[OrderResponse], status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    """Create an order for any subscription.
    
    Admin-only endpoint. Creates an order for any subscription.
    Note: In production, this would require admin authentication/authorization.
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
    
    order = order_repo.create(**order_data.model_dump())
    
    return Response(
        success=True,
        data=OrderResponse.model_validate(order),
        message="Order created successfully"
    )


@router.patch("/{order_id}", response_model=Response[OrderResponse], status_code=200)
def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
):
    """Update an order by ID (primarily status updates).
    
    Admin-only endpoint. Updates order fields (status, total_amount).
    Note: In production, this would require admin authentication/authorization.
    """
    order_repo = OrderRepository(db)
    
    order = order_repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in order_data.model_dump().items() if v is not None}
    
    if not update_data:
        return Response(
            success=True,
            data=OrderResponse.model_validate(order),
            message="No fields to update"
        )
    
    updated_order = order_repo.update(order_id, **update_data)
    
    return Response(
        success=True,
        data=OrderResponse.model_validate(updated_order),
        message="Order updated successfully"
    )


@router.get("/subscriptions/{subscription_id}/orders", response_model=PaginatedResponse[OrderResponse], status_code=200)
def get_subscription_orders(
    subscription_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get all orders for a specific subscription.
    
    Admin-only endpoint. Returns paginated list of orders for a subscription.
    Note: In production, this would require admin authentication/authorization.
    """
    order_repo = OrderRepository(db)
    subscription_repo = SubscriptionRepository(db)
    
    # Verify subscription exists
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail=f"Subscription with id {subscription_id} not found")
    
    orders = order_repo.get_by_subscription_id(subscription_id, skip=skip, limit=limit)
    total = order_repo.count_by_subscription_id(subscription_id)
    
    order_responses = [OrderResponse.model_validate(order) for order in orders]
    
    return PaginatedResponse(
        success=True,
        data=order_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


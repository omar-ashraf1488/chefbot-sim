"""Admin subscriptions API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
def list_subscriptions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    status: str | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all subscriptions with optional filtering.
    
    Admin-only endpoint. Returns paginated list of all subscriptions.
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    
    # Build filters
    filters = {}
    if user_id:
        # Verify user exists
        user_repo = UserRepository(db)
        user = user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        filters["user_id"] = user_id
    if status:
        filters["status"] = status
    
    subscriptions = subscription_repo.get_all(skip=skip, limit=limit, **filters)
    total = subscription_repo.count(**filters)
    
    subscription_responses = [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
    
    return PaginatedResponse(
        success=True,
        data=subscription_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/{subscription_id}", response_model=Response[SubscriptionResponse], status_code=200)
def get_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a subscription by ID.
    
    Admin-only endpoint. Returns subscription details by ID.
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    subscription = subscription_repo.get(subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    return Response(
        success=True,
        data=SubscriptionResponse.model_validate(subscription)
    )


@router.post("", response_model=Response[SubscriptionResponse], status_code=201)
def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    """Create a subscription for any user.
    
    Admin-only endpoint. Creates a subscription for any user.
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    
    # Verify user exists
    user_repo = UserRepository(db)
    user = user_repo.get(subscription_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {subscription_data.user_id} not found"
        )
    
    subscription = subscription_repo.create(**subscription_data.model_dump())
    
    return Response(
        success=True,
        data=SubscriptionResponse.model_validate(subscription),
        message="Subscription created successfully"
    )


@router.patch("/{subscription_id}", response_model=Response[SubscriptionResponse], status_code=200)
def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    """Update any subscription by ID.
    
    Admin-only endpoint. Updates subscription fields (status, preferences, etc.).
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in subscription_data.model_dump().items() if v is not None}
    
    if not update_data:
        return Response(
            success=True,
            data=SubscriptionResponse.model_validate(subscription),
            message="No fields to update"
        )
    
    updated_subscription = subscription_repo.update(subscription_id, **update_data)
    
    return Response(
        success=True,
        data=SubscriptionResponse.model_validate(updated_subscription),
        message="Subscription updated successfully"
    )


@router.delete("/{subscription_id}", status_code=204)
def cancel_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
):
    """Cancel any subscription (soft delete via status update).
    
    Admin-only endpoint. Cancels the subscription by setting status to Cancelled.
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # Update status to Cancelled
    subscription_repo.update(subscription_id, status="Cancelled")
    return None


@router.get("/users/{user_id}/subscriptions", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
def get_user_subscriptions(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get all subscriptions for a specific user.
    
    Admin-only endpoint. Returns paginated list of subscriptions for a user.
    Note: In production, this would require admin authentication/authorization.
    """
    subscription_repo = SubscriptionRepository(db)
    
    # Verify user exists
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    subscriptions = subscription_repo.get_by_user_id(user_id, skip=skip, limit=limit)
    total = subscription_repo.count_by_user_id(user_id)
    
    subscription_responses = [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
    
    return PaginatedResponse(
        success=True,
        data=subscription_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


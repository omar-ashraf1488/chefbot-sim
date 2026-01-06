"""User subscriptions API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate

router = APIRouter()


@router.get("/me/subscriptions", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
def get_my_subscriptions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    # user_id: UUID = Depends(get_current_user)  # Would be used with auth
):
    """Get current user's subscriptions.
    
    Authenticated endpoint. Returns paginated list of current user's subscriptions.
    Note: In production, this would require authentication to get the current user_id.
    This endpoint will be implemented when authentication is added.
    """
    # TODO: Get user_id from authenticated user when auth service is integrated
    # user_id = current_user.id
    
    raise HTTPException(
        status_code=501,
        detail="This endpoint requires authentication. Use /api/v1/subscriptions?user_id={uuid} for testing without auth."
    )


@router.get("", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
def get_subscriptions(
    user_id: UUID = Query(..., description="User ID to get subscriptions for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """Get subscriptions for a user (temporary endpoint for testing without auth).
    
    This endpoint is for testing purposes. In production, users would use /me/subscriptions
    which gets the user_id from the authentication token.
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


@router.post("", response_model=Response[SubscriptionResponse], status_code=201)
def create_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    """Create a subscription for current user.
    
    Authenticated endpoint. Creates a subscription for the authenticated user.
    Note: In production, user_id would come from the authenticated user, not the request body.
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


@router.get("/{subscription_id}", response_model=Response[SubscriptionResponse], status_code=200)
def get_subscription(
    subscription_id: UUID,
    db: Session = Depends(get_db),
    # user_id: UUID = Depends(get_current_user)  # Would verify ownership
):
    """Get a subscription by ID.
    
    Authenticated endpoint. Returns subscription details if the user owns it.
    Note: In production, this would verify the user owns the subscription.
    """
    subscription_repo = SubscriptionRepository(db)
    subscription = subscription_repo.get(subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # TODO: In production, verify user owns this subscription
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this subscription")
    
    return Response(
        success=True,
        data=SubscriptionResponse.model_validate(subscription)
    )


@router.patch("/{subscription_id}", response_model=Response[SubscriptionResponse], status_code=200)
def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    # user_id: UUID = Depends(get_current_user)  # Would verify ownership
):
    """Update a subscription by ID.
    
    Authenticated endpoint. Updates subscription (preferences, etc.) if the user owns it.
    Note: In production, this would verify the user owns the subscription.
    Status changes might require admin role.
    """
    subscription_repo = SubscriptionRepository(db)
    
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # TODO: In production, verify user owns this subscription
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this subscription")
    
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
    # user_id: UUID = Depends(get_current_user)  # Would verify ownership
):
    """Cancel a subscription (soft delete).
    
    Authenticated endpoint. Cancels the subscription if the user owns it.
    Note: In production, this would verify the user owns the subscription.
    """
    subscription_repo = SubscriptionRepository(db)
    
    subscription = subscription_repo.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail=f"Subscription with id {subscription_id} not found"
        )
    
    # TODO: In production, verify user owns this subscription
    # if subscription.user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Not authorized to cancel this subscription")
    
    # Update status to Cancelled instead of soft delete
    subscription_repo.update(subscription_id, status="Cancelled")
    return None


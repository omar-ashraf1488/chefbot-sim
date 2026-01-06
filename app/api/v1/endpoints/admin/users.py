"""Admin user management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository
from app.schemas.subscription import SubscriptionResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse], status_code=200)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """List all users with pagination.
    
    Admin-only endpoint. Returns paginated list of all users.
    """
    user_repo = UserRepository(db)
    users = user_repo.get_all(skip=skip, limit=limit)
    total = user_repo.count()
    
    user_responses = [UserResponse.model_validate(user) for user in users]
    
    return PaginatedResponse(
        success=True,
        data=user_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/{user_id}", response_model=Response[UserResponse], status_code=200)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a user by ID.
    
    Admin-only endpoint. Returns user details by ID.
    """
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    return Response(
        success=True,
        data=UserResponse.model_validate(user)
    )


@router.post("", response_model=Response[UserResponse], status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user.
    
    Admin-only endpoint. Creates a new user account.
    Note: In production, this would require admin authentication/authorization.
    """
    user_repo = UserRepository(db)
    
    # Check if user with email already exists
    existing_user = user_repo.get_by(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"User with email {user_data.email} already exists"
        )
    
    user = user_repo.create(**user_data.model_dump())
    
    return Response(
        success=True,
        data=UserResponse.model_validate(user),
        message="User created successfully"
    )


@router.patch("/{user_id}", response_model=Response[UserResponse], status_code=200)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    """Update a user by ID.
    
    Admin-only endpoint. Updates user fields (partial update).
    Note: In production, this would require admin authentication/authorization.
    """
    user_repo = UserRepository(db)
    
    # Check if user exists
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    # Check if email is being updated and if it conflicts with existing user
    if user_data.email is not None and user_data.email != user.email:
        existing_user = user_repo.get_by(email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with email {user_data.email} already exists"
            )
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    
    if not update_data:
        # No fields to update
        return Response(
            success=True,
            data=UserResponse.model_validate(user),
            message="No fields to update"
        )
    
    updated_user = user_repo.update(user_id, **update_data)
    
    return Response(
        success=True,
        data=UserResponse.model_validate(updated_user),
        message="User updated successfully"
    )


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a user by ID (soft delete).
    
    Admin-only endpoint. Soft deletes a user by setting deleted_at timestamp.
    Note: In production, this would require admin authentication/authorization.
    """
    user_repo = UserRepository(db)
    
    # Check if user exists
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    user_repo.soft_delete(user_id)
    return None


@router.get("/{user_id}/subscriptions", response_model=PaginatedResponse[SubscriptionResponse], status_code=200)
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
    user_repo = UserRepository(db)
    
    # Verify user exists
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    subscription_repo = SubscriptionRepository(db)
    subscriptions = subscription_repo.get_by_user_id(user_id, skip=skip, limit=limit)
    total = subscription_repo.count_by_user_id(user_id)
    
    subscription_responses = [SubscriptionResponse.model_validate(sub) for sub in subscriptions]
    
    return PaginatedResponse(
        success=True,
        data=subscription_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


"""Admin deliveries API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.schemas.delivery import DeliveryCreate, DeliveryResponse, DeliveryUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DeliveryResponse], status_code=200)
def list_deliveries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    order_id: UUID | None = Query(None, description="Filter by order ID"),
    status: str | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all deliveries with optional filtering.
    
    Admin-only endpoint. Returns paginated list of all deliveries.
    Note: In production, this would require admin authentication/authorization.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    
    # Build filters
    filters = {}
    if order_id:
        # Verify order exists
        order = order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
        filters["order_id"] = order_id
    if status:
        filters["status"] = status
    
    deliveries = delivery_repo.get_all(skip=skip, limit=limit, **filters)
    total = delivery_repo.count(**filters)
    
    delivery_responses = [DeliveryResponse.model_validate(delivery) for delivery in deliveries]
    
    return PaginatedResponse(
        success=True,
        data=delivery_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/{delivery_id}", response_model=Response[DeliveryResponse], status_code=200)
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a delivery by ID.
    
    Admin-only endpoint. Returns delivery details by ID.
    Note: In production, this would require admin authentication/authorization.
    """
    delivery_repo = DeliveryRepository(db)
    delivery = delivery_repo.get(delivery_id)
    
    if not delivery:
        raise HTTPException(status_code=404, detail=f"Delivery with id {delivery_id} not found")
    
    return Response(
        success=True,
        data=DeliveryResponse.model_validate(delivery)
    )


@router.post("", response_model=Response[DeliveryResponse], status_code=201)
def create_delivery(
    delivery_data: DeliveryCreate,
    db: Session = Depends(get_db),
):
    """Create a delivery for an order.
    
    Admin-only endpoint. Creates a delivery for an order.
    Note: In production, this would require admin authentication/authorization.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    
    # Verify order exists
    order = order_repo.get(delivery_data.order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Order with id {delivery_data.order_id} not found"
        )
    
    # Check if delivery already exists for this order (one-to-one relationship)
    existing_delivery = delivery_repo.get_by_order_id(delivery_data.order_id)
    if existing_delivery:
        raise HTTPException(
            status_code=400,
            detail=f"Delivery already exists for order {delivery_data.order_id}"
        )
    
    delivery = delivery_repo.create(**delivery_data.model_dump())
    
    return Response(
        success=True,
        data=DeliveryResponse.model_validate(delivery),
        message="Delivery created successfully"
    )


@router.patch("/{delivery_id}", response_model=Response[DeliveryResponse], status_code=200)
def update_delivery(
    delivery_id: UUID,
    delivery_data: DeliveryUpdate,
    db: Session = Depends(get_db),
):
    """Update a delivery by ID.
    
    Admin-only endpoint. Updates delivery fields (status, dates, tracking, notes).
    Note: In production, this would require admin authentication/authorization.
    """
    delivery_repo = DeliveryRepository(db)
    
    delivery = delivery_repo.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail=f"Delivery with id {delivery_id} not found")
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in delivery_data.model_dump().items() if v is not None}
    
    if not update_data:
        return Response(
            success=True,
            data=DeliveryResponse.model_validate(delivery),
            message="No fields to update"
        )
    
    updated_delivery = delivery_repo.update(delivery_id, **update_data)
    
    return Response(
        success=True,
        data=DeliveryResponse.model_validate(updated_delivery),
        message="Delivery updated successfully"
    )


@router.get("/orders/{order_id}/delivery", response_model=Response[DeliveryResponse], status_code=200)
def get_order_delivery(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """Get delivery for a specific order.
    
    Admin-only endpoint. Returns delivery for any order by order ID.
    Note: In production, this would require admin authentication/authorization.
    """
    delivery_repo = DeliveryRepository(db)
    order_repo = OrderRepository(db)
    
    # Verify order exists
    order = order_repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    
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


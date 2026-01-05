"""Unit tests for Delivery Pydantic schemas."""
import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.delivery import DeliveryCreate, DeliveryResponse


def test_delivery_create_valid():
    """Test creating a valid DeliveryCreate schema."""
    delivery_data = {
        "order_id": uuid4(),
        "status": "in_transit",
        "expected_delivery_date": datetime.now(),
        "actual_delivery_date": None,
        "tracking_number": "TRACK123456",
        "notes": "Left at front door"
    }
    delivery = DeliveryCreate(**delivery_data)
    
    assert delivery.order_id == delivery_data["order_id"]
    assert delivery.status == "in_transit"
    assert delivery.expected_delivery_date is not None
    assert delivery.actual_delivery_date is None
    assert delivery.tracking_number == "TRACK123456"
    assert delivery.notes == "Left at front door"


def test_delivery_create_invalid_status():
    """Test that invalid status values are rejected."""
    delivery_data = {
        "order_id": uuid4(),
        "status": "invalid_status",
        "expected_delivery_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        DeliveryCreate(**delivery_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("status",) for error in errors)


def test_delivery_create_all_valid_statuses():
    """Test that all valid status values are accepted."""
    valid_statuses = ["delivered", "delayed", "failed", "in_transit"]
    
    for status in valid_statuses:
        delivery_data = {
            "order_id": uuid4(),
            "status": status,
            "expected_delivery_date": datetime.now()
        }
        delivery = DeliveryCreate(**delivery_data)
        assert delivery.status == status


def test_delivery_create_nullable_fields():
    """Test that nullable fields can be None."""
    delivery_data = {
        "order_id": uuid4(),
        "status": "in_transit",
        "expected_delivery_date": datetime.now(),
        "actual_delivery_date": None,
        "tracking_number": None,
        "notes": None
    }
    delivery = DeliveryCreate(**delivery_data)
    
    assert delivery.actual_delivery_date is None
    assert delivery.tracking_number is None
    assert delivery.notes is None


def test_delivery_create_with_actual_delivery_date():
    """Test delivery with actual_delivery_date set."""
    delivery_data = {
        "order_id": uuid4(),
        "status": "delivered",
        "expected_delivery_date": datetime.now(),
        "actual_delivery_date": datetime.now()
    }
    delivery = DeliveryCreate(**delivery_data)
    
    assert delivery.status == "delivered"
    assert delivery.actual_delivery_date is not None


def test_delivery_create_missing_required_fields():
    """Test that missing required fields are rejected."""
    # Missing order_id
    with pytest.raises(ValidationError):
        DeliveryCreate(
            status="in_transit",
            expected_delivery_date=datetime.now()
        )
    
    # Missing status
    with pytest.raises(ValidationError):
        DeliveryCreate(
            order_id=uuid4(),
            expected_delivery_date=datetime.now()
        )
    
    # Missing expected_delivery_date
    with pytest.raises(ValidationError):
        DeliveryCreate(
            order_id=uuid4(),
            status="in_transit"
        )


def test_delivery_response_valid():
    """Test creating a valid DeliveryResponse schema."""
    delivery_data = {
        "id": uuid4(),
        "order_id": uuid4(),
        "status": "delivered",
        "expected_delivery_date": datetime.now(),
        "actual_delivery_date": datetime.now(),
        "tracking_number": "TRACK123456",
        "notes": "Delivered successfully",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    delivery = DeliveryResponse(**delivery_data)
    
    assert delivery.id == delivery_data["id"]
    assert delivery.order_id == delivery_data["order_id"]
    assert delivery.status == "delivered"
    assert delivery.expected_delivery_date is not None
    assert delivery.actual_delivery_date is not None
    assert delivery.tracking_number == "TRACK123456"
    assert delivery.notes == "Delivered successfully"
    assert delivery.created_at is not None
    assert delivery.updated_at is not None


def test_delivery_response_with_nullable_fields():
    """Test DeliveryResponse with all nullable fields as None."""
    delivery_data = {
        "id": uuid4(),
        "order_id": uuid4(),
        "status": "in_transit",
        "expected_delivery_date": datetime.now(),
        "actual_delivery_date": None,
        "tracking_number": None,
        "notes": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    delivery = DeliveryResponse(**delivery_data)
    
    assert delivery.status == "in_transit"
    assert delivery.actual_delivery_date is None
    assert delivery.tracking_number is None
    assert delivery.notes is None


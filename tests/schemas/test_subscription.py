"""Unit tests for Subscription Pydantic schemas."""
import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse


def test_subscription_create_valid():
    """Test creating a valid SubscriptionCreate schema."""
    subscription_data = {
        "user_id": uuid4(),
        "status": "Active",
        "preferences": {"No Fish": True, "Vegan": False},
        "started_at": datetime.now()
    }
    subscription = SubscriptionCreate(**subscription_data)
    
    assert subscription.user_id == subscription_data["user_id"]
    assert subscription.status == "Active"
    assert subscription.preferences == {"No Fish": True, "Vegan": False}
    assert subscription.started_at is not None


def test_subscription_create_invalid_status():
    """Test that invalid status values are rejected."""
    subscription_data = {
        "user_id": uuid4(),
        "status": "InvalidStatus",
        "preferences": None,
        "started_at": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        SubscriptionCreate(**subscription_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("status",) for error in errors)


def test_subscription_create_all_valid_statuses():
    """Test that all valid status values are accepted."""
    valid_statuses = ["Active", "Paused", "Cancelled"]
    
    for status in valid_statuses:
        subscription_data = {
            "user_id": uuid4(),
            "status": status,
            "preferences": None,
            "started_at": datetime.now()
        }
        subscription = SubscriptionCreate(**subscription_data)
        assert subscription.status == status


def test_subscription_create_invalid_preferences():
    """Test that non-dict preferences are rejected."""
    subscription_data = {
        "user_id": uuid4(),
        "status": "Active",
        "preferences": "not-a-dict",  # Should be dict or None
        "started_at": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        SubscriptionCreate(**subscription_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("preferences",) for error in errors)


def test_subscription_create_preferences_nullable():
    """Test that preferences can be None."""
    subscription_data = {
        "user_id": uuid4(),
        "status": "Active",
        "preferences": None,
        "started_at": datetime.now()
    }
    subscription = SubscriptionCreate(**subscription_data)
    
    assert subscription.preferences is None


def test_subscription_create_valid_preferences_formats():
    """Test different valid preference formats."""
    test_cases = [
        # Boolean values
        {"No Fish": True, "Vegan": False},
        # String values
        {"Dietary Restriction": "Gluten Free", "Allergy": "Peanuts"},
        # Mixed bool and str values
        {"No Fish": True, "Vegan": False, "Dietary Note": "Low Sodium"},
        # Empty dict
        {},
    ]
    
    for preferences in test_cases:
        subscription_data = {
            "user_id": uuid4(),
            "status": "Active",
            "preferences": preferences,
            "started_at": datetime.now()
        }
        subscription = SubscriptionCreate(**subscription_data)
        assert subscription.preferences == preferences


def test_subscription_create_missing_required_fields():
    """Test that missing required fields are rejected."""
    # Missing user_id
    with pytest.raises(ValidationError):
        SubscriptionCreate(
            status="Active",
            started_at=datetime.now()
        )
    
    # Missing status
    with pytest.raises(ValidationError):
        SubscriptionCreate(
            user_id=uuid4(),
            started_at=datetime.now()
        )
    
    # Missing started_at
    with pytest.raises(ValidationError):
        SubscriptionCreate(
            user_id=uuid4(),
            status="Active"
        )


def test_subscription_response_valid():
    """Test creating a valid SubscriptionResponse schema."""
    subscription_data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "status": "Active",
        "preferences": {"No Fish": True},
        "started_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    subscription = SubscriptionResponse(**subscription_data)
    
    assert subscription.id == subscription_data["id"]
    assert subscription.user_id == subscription_data["user_id"]
    assert subscription.status == "Active"
    assert subscription.preferences == {"No Fish": True}
    assert subscription.started_at is not None
    assert subscription.created_at is not None
    assert subscription.updated_at is not None


def test_subscription_response_with_nullable_preferences():
    """Test SubscriptionResponse with None preferences."""
    subscription_data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "status": "Paused",
        "preferences": None,
        "started_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    subscription = SubscriptionResponse(**subscription_data)
    
    assert subscription.status == "Paused"
    assert subscription.preferences is None


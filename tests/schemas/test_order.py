"""Unit tests for Order Pydantic schemas."""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.order import OrderCreate, OrderResponse


def test_order_create_valid():
    """Test creating a valid OrderCreate schema."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": [{"id": str(uuid4()), "name": "Pasta Carbonara"}],
        "total_amount": Decimal("49.98"),
        "status": "pending",
        "order_date": datetime.now()
    }
    order = OrderCreate(**order_data)
    
    assert order.subscription_id == order_data["subscription_id"]
    assert order.recipes == order_data["recipes"]
    assert order.total_amount == Decimal("49.98")
    assert order.status == "pending"
    assert order.order_date is not None


def test_order_create_invalid_status():
    """Test that invalid status values are rejected."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": [{"id": str(uuid4()), "name": "Recipe"}],
        "total_amount": Decimal("25.00"),
        "status": "invalid_status",
        "order_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(**order_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("status",) for error in errors)


def test_order_create_all_valid_statuses():
    """Test that all valid status values are accepted."""
    valid_statuses = ["pending", "shipped", "delivered", "cancelled"]
    
    for status in valid_statuses:
        order_data = {
            "subscription_id": uuid4(),
            "recipes": [{"id": str(uuid4()), "name": "Recipe"}],
            "total_amount": Decimal("25.00"),
            "status": status,
            "order_date": datetime.now()
        }
        order = OrderCreate(**order_data)
        assert order.status == status


def test_order_create_invalid_total_amount_negative():
    """Test that negative total_amount is rejected."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": [{"id": str(uuid4()), "name": "Recipe"}],
        "total_amount": Decimal("-10.00"),
        "status": "pending",
        "order_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(**order_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("total_amount",) for error in errors)


def test_order_create_invalid_recipes_empty():
    """Test that empty recipes list is rejected."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": [],
        "total_amount": Decimal("25.00"),
        "status": "pending",
        "order_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(**order_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("recipes",) for error in errors)


def test_order_create_invalid_recipes_not_list():
    """Test that non-list recipes are rejected."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": "not-a-list",
        "total_amount": Decimal("25.00"),
        "status": "pending",
        "order_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(**order_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("recipes",) for error in errors)


def test_order_create_invalid_recipes_not_dicts():
    """Test that recipes with non-dict elements are rejected."""
    order_data = {
        "subscription_id": uuid4(),
        "recipes": ["not-a-dict", {"id": "uuid", "name": "Recipe"}],
        "total_amount": Decimal("25.00"),
        "status": "pending",
        "order_date": datetime.now()
    }
    
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(**order_data)
    
    errors = exc_info.value.errors()
    # Check if any error is related to recipes (could be ("recipes",) or ("recipes", index))
    assert any("recipes" in error["loc"] for error in errors)


def test_order_create_valid_recipes_formats():
    """Test different valid recipe formats."""
    test_cases = [
        [{"id": "uuid1", "name": "Recipe 1"}],
        [{"id": "uuid1", "name": "Recipe 1"}, {"id": "uuid2", "name": "Recipe 2"}],
        [{"id": "uuid1", "name": "Recipe 1", "quantity": 2}],
    ]
    
    for recipes in test_cases:
        order_data = {
            "subscription_id": uuid4(),
            "recipes": recipes,
            "total_amount": Decimal("25.00"),
            "status": "pending",
            "order_date": datetime.now()
        }
        order = OrderCreate(**order_data)
        assert order.recipes == recipes


def test_order_create_missing_required_fields():
    """Test that missing required fields are rejected."""
    # Missing subscription_id
    with pytest.raises(ValidationError):
        OrderCreate(
            recipes=[{"id": "uuid", "name": "Recipe"}],
            total_amount=Decimal("25.00"),
            status="pending",
            order_date=datetime.now()
        )
    
    # Missing recipes
    with pytest.raises(ValidationError):
        OrderCreate(
            subscription_id=uuid4(),
            total_amount=Decimal("25.00"),
            status="pending",
            order_date=datetime.now()
        )
    
    # Missing total_amount
    with pytest.raises(ValidationError):
        OrderCreate(
            subscription_id=uuid4(),
            recipes=[{"id": "uuid", "name": "Recipe"}],
            status="pending",
            order_date=datetime.now()
        )
    
    # Missing status
    with pytest.raises(ValidationError):
        OrderCreate(
            subscription_id=uuid4(),
            recipes=[{"id": "uuid", "name": "Recipe"}],
            total_amount=Decimal("25.00"),
            order_date=datetime.now()
        )
    
    # Missing order_date
    with pytest.raises(ValidationError):
        OrderCreate(
            subscription_id=uuid4(),
            recipes=[{"id": "uuid", "name": "Recipe"}],
            total_amount=Decimal("25.00"),
            status="pending"
        )


def test_order_response_valid():
    """Test creating a valid OrderResponse schema."""
    order_data = {
        "id": uuid4(),
        "subscription_id": uuid4(),
        "recipes": [{"id": str(uuid4()), "name": "Recipe"}],
        "total_amount": Decimal("49.98"),
        "status": "shipped",
        "order_date": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    order = OrderResponse(**order_data)
    
    assert order.id == order_data["id"]
    assert order.subscription_id == order_data["subscription_id"]
    assert order.recipes == order_data["recipes"]
    assert order.total_amount == Decimal("49.98")
    assert order.status == "shipped"
    assert order.order_date is not None
    assert order.created_at is not None
    assert order.updated_at is not None


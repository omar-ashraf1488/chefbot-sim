"""Tests for admin orders API endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_list_orders_empty(client: TestClient, db_session):
    """Test listing orders when database is empty."""
    response = client.get("/api/v1/admin/orders")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_list_orders_with_pagination(client: TestClient, db_session):
    """Test listing orders with pagination."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    # Create 5 orders
    for i in range(5):
        order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending" if i % 2 == 0 else "shipped",
            order_date=datetime.now(timezone.utc)
        )
    
    response = client.get("/api/v1/admin/orders?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5


def test_list_orders_filter_by_subscription_id(client: TestClient, db_session):
    """Test filtering orders by subscription_id."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription1 = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    subscription2 = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    # Create orders for both subscriptions
    order_repo.create(
        subscription_id=subscription1.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    order_repo.create(
        subscription_id=subscription1.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 2"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    order_repo.create(
        subscription_id=subscription2.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 3"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/admin/orders?subscription_id={subscription1.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 2
    assert all(order["subscription_id"] == str(subscription1.id) for order in data["data"])


def test_list_orders_filter_by_status(client: TestClient, db_session):
    """Test filtering orders by status."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    # Create orders with different statuses
    order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 2"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 3"}],
        total_amount=Decimal("29.99"),
        status="shipped",
        order_date=datetime.now(timezone.utc)
    )
    
    response = client.get("/api/v1/admin/orders?status=pending")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 2
    assert all(order["status"] == "pending" for order in data["data"])


def test_list_orders_subscription_not_found_filter(client: TestClient, db_session):
    """Test filtering by non-existent subscription_id."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/orders?subscription_id={fake_id}")
    
    assert response.status_code == 404


def test_get_order_success(client: TestClient, db_session):
    """Test getting an order by ID."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    order = order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Test Recipe"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/admin/orders/{order.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(order.id)
    assert data["data"]["subscription_id"] == str(subscription.id)
    assert data["data"]["status"] == "pending"


def test_get_order_not_found(client: TestClient, db_session):
    """Test getting an order that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/orders/{fake_id}")
    
    assert response.status_code == 404


def test_create_order_success(client: TestClient, db_session):
    """Test creating an order successfully."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    order_data = {
        "subscription_id": str(subscription.id),
        "recipes": [{"id": str(uuid4()), "name": "Recipe 1"}],
        "total_amount": "29.99",
        "status": "pending",
        "order_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/orders", json=order_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["subscription_id"] == str(subscription.id)
    assert data["data"]["status"] == "pending"
    assert data["message"] == "Order created successfully"


def test_create_order_subscription_not_found(client: TestClient, db_session):
    """Test creating order for non-existent subscription."""
    fake_id = uuid4()
    
    order_data = {
        "subscription_id": str(fake_id),
        "recipes": [{"id": str(uuid4()), "name": "Recipe 1"}],
        "total_amount": "29.99",
        "status": "pending",
        "order_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/orders", json=order_data)
    
    assert response.status_code == 404


def test_update_order_success(client: TestClient, db_session):
    """Test updating an order successfully."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    order = order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    update_data = {
        "status": "shipped"
    }
    
    response = client.patch(f"/api/v1/admin/orders/{order.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["status"] == "shipped"
    assert data["message"] == "Order updated successfully"


def test_update_order_status_all_transitions(client: TestClient, db_session):
    """Test updating order status through different states."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    order = order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    # Test status transitions
    for status in ["shipped", "delivered"]:
        update_data = {"status": status}
        response = client.patch(f"/api/v1/admin/orders/{order.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["data"]["status"] == status


def test_update_order_not_found(client: TestClient, db_session):
    """Test updating an order that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "status": "shipped"
    }
    
    response = client.patch(f"/api/v1/admin/orders/{fake_id}", json=update_data)
    
    assert response.status_code == 404


def test_get_subscription_orders(client: TestClient, db_session):
    """Test getting all orders for a specific subscription."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription = subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    
    # Create 3 orders
    for i in range(3):
        order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
    
    response = client.get(f"/api/v1/admin/orders/subscriptions/{subscription.id}/orders")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 3
    assert all(order["subscription_id"] == str(subscription.id) for order in data["data"])


def test_get_subscription_orders_not_found(client: TestClient, db_session):
    """Test getting orders for non-existent subscription."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/orders/subscriptions/{fake_id}/orders")
    
    assert response.status_code == 404


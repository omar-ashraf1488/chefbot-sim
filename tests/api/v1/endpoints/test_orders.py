"""Tests for user orders API endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_get_orders_empty(client: TestClient, db_session):
    """Test getting orders when user has none."""
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
    
    response = client.get(f"/api/v1/orders?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_get_orders_with_subscription(client: TestClient, db_session):
    """Test getting orders for a user with subscriptions."""
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
    
    # Create 3 orders for this subscription
    for i in range(3):
        order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
    
    response = client.get(f"/api/v1/orders?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_orders_user_not_found(client: TestClient, db_session):
    """Test getting orders for non-existent user."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/orders?user_id={fake_id}")
    
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
    
    response = client.post("/api/v1/orders", json=order_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["subscription_id"] == str(subscription.id)
    assert data["data"]["status"] == "pending"
    assert float(data["data"]["total_amount"]) == 29.99
    assert len(data["data"]["recipes"]) == 1
    assert data["message"] == "Order created successfully"


def test_create_order_invalid_status(client: TestClient, db_session):
    """Test creating an order with invalid status."""
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
        "status": "InvalidStatus",
        "order_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/orders", json=order_data)
    
    assert response.status_code == 422  # Validation error


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
    
    response = client.post("/api/v1/orders", json=order_data)
    
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
    
    response = client.get(f"/api/v1/orders/{order.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(order.id)
    assert data["data"]["subscription_id"] == str(subscription.id)
    assert data["data"]["status"] == "pending"


def test_get_order_not_found(client: TestClient, db_session):
    """Test getting an order that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/orders/{fake_id}")
    
    assert response.status_code == 404


def test_get_subscription_orders(client: TestClient, db_session):
    """Test getting orders for a subscription."""
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
    
    response = client.get(f"/api/v1/orders/subscriptions/{subscription.id}/orders")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 3
    assert all(order["subscription_id"] == str(subscription.id) for order in data["data"])


def test_get_subscription_orders_not_found(client: TestClient, db_session):
    """Test getting orders for non-existent subscription."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/orders/subscriptions/{fake_id}/orders")
    
    assert response.status_code == 404


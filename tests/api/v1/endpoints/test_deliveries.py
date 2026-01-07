"""Tests for user deliveries API endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_get_deliveries_empty(client: TestClient, db_session):
    """Test getting deliveries when user has none."""
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
    
    response = client.get(f"/api/v1/deliveries?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_get_deliveries_with_orders(client: TestClient, db_session):
    """Test getting deliveries for a user with orders."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    delivery_repo = DeliveryRepository(db_session)
    
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
    
    # Create 3 orders with deliveries
    for i in range(3):
        order = order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
        
        delivery_repo.create(
            order_id=order.id,
            status="in_transit",
            expected_delivery_date=datetime.now(timezone.utc),
            tracking_number=f"TRACK{i}"
        )
    
    response = client.get(f"/api/v1/deliveries?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3
    assert all(delivery["status"] == "in_transit" for delivery in data["data"])


def test_get_deliveries_user_not_found(client: TestClient, db_session):
    """Test getting deliveries for non-existent user."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/deliveries?user_id={fake_id}")
    
    assert response.status_code == 404


def test_get_deliveries_only_returns_deliveries_with_orders(client: TestClient, db_session):
    """Test that only orders with deliveries are returned."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    delivery_repo = DeliveryRepository(db_session)
    
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
    
    # Create 3 orders, but only 2 have deliveries
    orders = []
    for i in range(3):
        order = order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
        orders.append(order)
        
        # Only create delivery for first 2 orders
        if i < 2:
            delivery_repo.create(
                order_id=order.id,
                status="in_transit",
                expected_delivery_date=datetime.now(timezone.utc),
                tracking_number=f"TRACK{i}"
            )
    
    response = client.get(f"/api/v1/deliveries?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2  # Only 2 deliveries
    assert data["pagination"]["total"] == 2


def test_get_order_delivery_success(client: TestClient, db_session):
    """Test getting delivery for an order by order ID."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    order_repo = OrderRepository(db_session)
    delivery_repo = DeliveryRepository(db_session)
    
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
    
    delivery = delivery_repo.create(
        order_id=order.id,
        status="delivered",
        expected_delivery_date=datetime.now(timezone.utc),
        actual_delivery_date=datetime.now(timezone.utc),
        tracking_number="TRACK123"
    )
    
    response = client.get(f"/api/v1/deliveries/orders/{order.id}/delivery")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(delivery.id)
    assert data["data"]["order_id"] == str(order.id)
    assert data["data"]["status"] == "delivered"
    assert data["data"]["tracking_number"] == "TRACK123"


def test_get_order_delivery_order_not_found(client: TestClient, db_session):
    """Test getting delivery for non-existent order."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/deliveries/orders/{fake_id}/delivery")
    
    assert response.status_code == 404


def test_get_order_delivery_no_delivery(client: TestClient, db_session):
    """Test getting delivery when order exists but has no delivery."""
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
    
    response = client.get(f"/api/v1/deliveries/orders/{order.id}/delivery")
    
    assert response.status_code == 404
    assert "delivery" in response.json()["detail"].lower()


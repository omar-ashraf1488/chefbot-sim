"""Tests for admin deliveries API endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_list_deliveries_empty(client: TestClient, db_session):
    """Test listing deliveries when database is empty."""
    response = client.get("/api/v1/admin/deliveries")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_list_deliveries_with_pagination(client: TestClient, db_session):
    """Test listing deliveries with pagination."""
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
    
    # Create 5 orders with deliveries
    for i in range(5):
        order = order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
        
        delivery_repo.create(
            order_id=order.id,
            status="in_transit" if i % 2 == 0 else "delivered",
            expected_delivery_date=datetime.now(timezone.utc),
            tracking_number=f"TRACK{i}"
        )
    
    response = client.get("/api/v1/admin/deliveries?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5


def test_list_deliveries_filter_by_order_id(client: TestClient, db_session):
    """Test filtering deliveries by order_id."""
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
    
    order1 = order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    order2 = order_repo.create(
        subscription_id=subscription.id,
        recipes=[{"id": str(uuid4()), "name": "Recipe 2"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    delivery1 = delivery_repo.create(
        order_id=order1.id,
        status="in_transit",
        expected_delivery_date=datetime.now(timezone.utc),
        tracking_number="TRACK1"
    )
    
    delivery_repo.create(
        order_id=order2.id,
        status="delivered",
        expected_delivery_date=datetime.now(timezone.utc),
        tracking_number="TRACK2"
    )
    
    response = client.get(f"/api/v1/admin/deliveries?order_id={order1.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 1
    assert data["data"][0]["id"] == str(delivery1.id)
    assert data["data"][0]["order_id"] == str(order1.id)


def test_list_deliveries_filter_by_status(client: TestClient, db_session):
    """Test filtering deliveries by status."""
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
    
    # Create deliveries with different statuses
    for i, status in enumerate(["in_transit", "in_transit", "delivered"]):
        order = order_repo.create(
            subscription_id=subscription.id,
            recipes=[{"id": str(uuid4()), "name": f"Recipe {i}"}],
            total_amount=Decimal("29.99"),
            status="pending",
            order_date=datetime.now(timezone.utc)
        )
        
        delivery_repo.create(
            order_id=order.id,
            status=status,
            expected_delivery_date=datetime.now(timezone.utc),
            tracking_number=f"TRACK{i}"
        )
    
    response = client.get("/api/v1/admin/deliveries?status=in_transit")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 2
    assert all(delivery["status"] == "in_transit" for delivery in data["data"])


def test_list_deliveries_order_not_found_filter(client: TestClient, db_session):
    """Test filtering by non-existent order_id."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/deliveries?order_id={fake_id}")
    
    assert response.status_code == 404


def test_get_delivery_success(client: TestClient, db_session):
    """Test getting a delivery by ID."""
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
    
    response = client.get(f"/api/v1/admin/deliveries/{delivery.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(delivery.id)
    assert data["data"]["order_id"] == str(order.id)
    assert data["data"]["status"] == "delivered"


def test_get_delivery_not_found(client: TestClient, db_session):
    """Test getting a delivery that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/deliveries/{fake_id}")
    
    assert response.status_code == 404


def test_create_delivery_success(client: TestClient, db_session):
    """Test creating a delivery successfully."""
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
    
    delivery_data = {
        "order_id": str(order.id),
        "status": "in_transit",
        "expected_delivery_date": datetime.now(timezone.utc).isoformat(),
        "tracking_number": "TRACK123",
        "notes": "Out for delivery"
    }
    
    response = client.post("/api/v1/admin/deliveries", json=delivery_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["order_id"] == str(order.id)
    assert data["data"]["status"] == "in_transit"
    assert data["data"]["tracking_number"] == "TRACK123"
    assert data["message"] == "Delivery created successfully"


def test_create_delivery_order_not_found(client: TestClient, db_session):
    """Test creating delivery for non-existent order."""
    fake_id = uuid4()
    
    delivery_data = {
        "order_id": str(fake_id),
        "status": "in_transit",
        "expected_delivery_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/deliveries", json=delivery_data)
    
    assert response.status_code == 404


def test_create_delivery_duplicate(client: TestClient, db_session):
    """Test creating duplicate delivery for same order (one-to-one relationship)."""
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
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    # Create first delivery
    delivery_repo.create(
        order_id=order.id,
        status="in_transit",
        expected_delivery_date=datetime.now(timezone.utc)
    )
    
    # Try to create duplicate
    delivery_data = {
        "order_id": str(order.id),
        "status": "delivered",
        "expected_delivery_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/deliveries", json=delivery_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_update_delivery_success(client: TestClient, db_session):
    """Test updating a delivery successfully."""
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
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    delivery = delivery_repo.create(
        order_id=order.id,
        status="in_transit",
        expected_delivery_date=datetime.now(timezone.utc),
        tracking_number="TRACK123"
    )
    
    update_data = {
        "status": "delivered",
        "actual_delivery_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.patch(f"/api/v1/admin/deliveries/{delivery.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["status"] == "delivered"
    assert data["data"]["actual_delivery_date"] is not None
    assert data["message"] == "Delivery updated successfully"


def test_update_delivery_all_fields(client: TestClient, db_session):
    """Test updating all delivery fields."""
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
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    delivery = delivery_repo.create(
        order_id=order.id,
        status="in_transit",
        expected_delivery_date=datetime.now(timezone.utc),
        tracking_number="OLD123"
    )
    
    new_date = datetime.now(timezone.utc)
    update_data = {
        "status": "delivered",
        "expected_delivery_date": new_date.isoformat(),
        "actual_delivery_date": new_date.isoformat(),
        "tracking_number": "NEW456",
        "notes": "Delivered to front door"
    }
    
    response = client.patch(f"/api/v1/admin/deliveries/{delivery.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["status"] == "delivered"
    assert data["data"]["tracking_number"] == "NEW456"
    assert data["data"]["notes"] == "Delivered to front door"


def test_update_delivery_not_found(client: TestClient, db_session):
    """Test updating a delivery that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "status": "delivered"
    }
    
    response = client.patch(f"/api/v1/admin/deliveries/{fake_id}", json=update_data)
    
    assert response.status_code == 404


def test_get_order_delivery(client: TestClient, db_session):
    """Test getting delivery for a specific order."""
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
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    delivery = delivery_repo.create(
        order_id=order.id,
        status="delivered",
        expected_delivery_date=datetime.now(timezone.utc),
        tracking_number="TRACK123"
    )
    
    response = client.get(f"/api/v1/admin/deliveries/orders/{order.id}/delivery")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(delivery.id)
    assert data["data"]["order_id"] == str(order.id)


def test_get_order_delivery_order_not_found(client: TestClient, db_session):
    """Test getting delivery for non-existent order."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/deliveries/orders/{fake_id}/delivery")
    
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
        recipes=[{"id": str(uuid4()), "name": "Recipe 1"}],
        total_amount=Decimal("29.99"),
        status="pending",
        order_date=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/admin/deliveries/orders/{order.id}/delivery")
    
    assert response.status_code == 404


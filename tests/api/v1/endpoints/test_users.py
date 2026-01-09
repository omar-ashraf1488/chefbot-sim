"""Tests for user profile API endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.delivery_repository import DeliveryRepository
from app.core.repositories.order_repository import OrderRepository
from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_get_current_user_success(client: TestClient, db_session):
    """Test getting current user profile successfully."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    response = client.get(f"/api/v1/users/me?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(user.id)
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["first_name"] == "Test"
    assert data["data"]["last_name"] == "User"


def test_get_current_user_not_found(client: TestClient, db_session):
    """Test getting current user when user doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/users/me?user_id={fake_id}")
    
    assert response.status_code == 404


def test_get_current_user_missing_user_id(client: TestClient, db_session):
    """Test getting current user without user_id parameter."""
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == 422  # Validation error


def test_update_current_user_success(client: TestClient, db_session):
    """Test updating current user profile successfully."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "timezone": "America/New_York"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["first_name"] == "Updated"
    assert data["data"]["last_name"] == "Name"
    assert data["data"]["timezone"] == "America/New_York"
    assert data["data"]["email"] == "test@example.com"  # Unchanged
    assert data["message"] == "Profile updated successfully"


def test_update_current_user_partial(client: TestClient, db_session):
    """Test partial update of current user profile."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "first_name": "Updated"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["first_name"] == "Updated"
    assert data["data"]["last_name"] == "User"  # Unchanged
    assert data["data"]["email"] == "test@example.com"  # Unchanged


def test_update_current_user_email(client: TestClient, db_session):
    """Test updating current user email successfully."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "email": "newemail@example.com"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["email"] == "newemail@example.com"


def test_update_current_user_email_duplicate(client: TestClient, db_session):
    """Test updating current user email to an already used email."""
    user_repo = UserRepository(db_session)
    
    user1 = user_repo.create(
        email="test1@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    user2 = user_repo.create(
        email="test2@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "email": "test2@example.com"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user1.id}", json=update_data)
    
    assert response.status_code == 409  # ConflictError
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "message" in data["error"]
    assert "already" in data["error"]["message"].lower() or "conflict" in data["error"]["message"].lower()


def test_update_current_user_email_same(client: TestClient, db_session):
    """Test updating current user email to the same email (should succeed)."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "email": "test@example.com"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_update_current_user_no_fields(client: TestClient, db_session):
    """Test updating current user with no fields provided."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {}
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "No fields to update" in data["message"]


def test_update_current_user_invalid_timezone(client: TestClient, db_session):
    """Test updating current user with invalid timezone."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    update_data = {
        "timezone": "Invalid/Timezone"
    }
    
    response = client.patch(f"/api/v1/users/me?user_id={user.id}", json=update_data)
    
    assert response.status_code == 422  # Validation error


def test_delete_current_user_success(client: TestClient, db_session):
    """Test deleting current user account (soft delete)."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    response = client.delete(f"/api/v1/users/me?user_id={user.id}")
    
    assert response.status_code == 204
    
    # Verify user is soft deleted
    deleted_user = user_repo.get(user.id)
    assert deleted_user is None
    
    # Verify user still exists in database (soft delete)
    from sqlalchemy import select
    from app.models.user import User
    stmt = select(User).filter_by(id=user.id)
    db_user = db_session.scalar(stmt)
    assert db_user is not None
    assert db_user.deleted_at is not None


def test_delete_current_user_not_found(client: TestClient, db_session):
    """Test deleting current user when user doesn't exist."""
    fake_id = uuid4()
    
    response = client.delete(f"/api/v1/users/me?user_id={fake_id}")
    
    assert response.status_code == 404


def test_get_current_user_subscriptions_success(client: TestClient, db_session):
    """Test getting current user's subscriptions."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create 3 subscriptions
    for i in range(3):
        subscription_repo.create(
            user_id=user.id,
            status="Active",
            started_at=datetime.now(timezone.utc)
        )
    
    response = client.get(f"/api/v1/users/me/subscriptions?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_current_user_subscriptions_empty(client: TestClient, db_session):
    """Test getting current user's subscriptions when user has none."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    response = client.get(f"/api/v1/users/me/subscriptions?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_get_current_user_subscriptions_filter_by_status(client: TestClient, db_session):
    """Test filtering current user's subscriptions by status."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create subscriptions with different statuses
    subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    subscription_repo.create(
        user_id=user.id,
        status="Active",
        started_at=datetime.now(timezone.utc)
    )
    subscription_repo.create(
        user_id=user.id,
        status="Cancelled",
        started_at=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/users/me/subscriptions?user_id={user.id}&status=Active")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert all(sub["status"] == "Active" for sub in data["data"])


def test_get_current_user_orders_success(client: TestClient, db_session):
    """Test getting current user's orders."""
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
    
    response = client.get(f"/api/v1/users/me/orders?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_current_user_orders_filter_by_status(client: TestClient, db_session):
    """Test filtering current user's orders by status."""
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
    
    response = client.get(f"/api/v1/users/me/orders?user_id={user.id}&status=pending")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert all(order["status"] == "pending" for order in data["data"])


def test_get_current_user_deliveries_success(client: TestClient, db_session):
    """Test getting current user's deliveries."""
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
    
    response = client.get(f"/api/v1/users/me/deliveries?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_current_user_deliveries_filter_by_status(client: TestClient, db_session):
    """Test filtering current user's deliveries by status."""
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
    
    response = client.get(f"/api/v1/users/me/deliveries?user_id={user.id}&status=in_transit")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert all(delivery["status"] == "in_transit" for delivery in data["data"])


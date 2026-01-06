"""Tests for admin subscriptions API endpoints."""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_list_subscriptions_empty(client: TestClient, db_session):
    """Test listing subscriptions when database is empty."""
    response = client.get("/api/v1/admin/subscriptions")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_list_subscriptions_with_pagination(client: TestClient, db_session):
    """Test listing subscriptions with pagination."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create 5 subscriptions
    for i in range(5):
        subscription_repo.create(
            user_id=user.id,
            status="Active" if i % 2 == 0 else "Paused",
            started_at=datetime.now(timezone.utc)
        )
    
    response = client.get("/api/v1/admin/subscriptions?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5


def test_list_subscriptions_filter_by_user_id(client: TestClient, db_session):
    """Test filtering subscriptions by user_id."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user1 = user_repo.create(
        email="user1@example.com",
        first_name="User",
        last_name="One",
        timezone="UTC"
    )
    
    user2 = user_repo.create(
        email="user2@example.com",
        first_name="User",
        last_name="Two",
        timezone="UTC"
    )
    
    # Create subscriptions for both users
    subscription_repo.create(user_id=user1.id, status="Active", started_at=datetime.now(timezone.utc))
    subscription_repo.create(user_id=user1.id, status="Active", started_at=datetime.now(timezone.utc))
    subscription_repo.create(user_id=user2.id, status="Active", started_at=datetime.now(timezone.utc))
    
    response = client.get(f"/api/v1/admin/subscriptions?user_id={user1.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 2
    assert all(sub["user_id"] == str(user1.id) for sub in data["data"])


def test_list_subscriptions_filter_by_status(client: TestClient, db_session):
    """Test filtering subscriptions by status."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create subscriptions with different statuses
    subscription_repo.create(user_id=user.id, status="Active", started_at=datetime.now(timezone.utc))
    subscription_repo.create(user_id=user.id, status="Active", started_at=datetime.now(timezone.utc))
    subscription_repo.create(user_id=user.id, status="Paused", started_at=datetime.now(timezone.utc))
    
    response = client.get("/api/v1/admin/subscriptions?status=Active")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 2
    assert all(sub["status"] == "Active" for sub in data["data"])


def test_list_subscriptions_user_not_found_filter(client: TestClient, db_session):
    """Test filtering by non-existent user_id."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/subscriptions?user_id={fake_id}")
    
    assert response.status_code == 404


def test_get_subscription_success(client: TestClient, db_session):
    """Test getting a subscription by ID."""
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
        preferences={"Vegan": True},
        started_at=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/admin/subscriptions/{subscription.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(subscription.id)
    assert data["data"]["user_id"] == str(user.id)
    assert data["data"]["status"] == "Active"


def test_get_subscription_not_found(client: TestClient, db_session):
    """Test getting a subscription that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/subscriptions/{fake_id}")
    
    assert response.status_code == 404


def test_create_subscription_success(client: TestClient, db_session):
    """Test creating a subscription successfully."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription_data = {
        "user_id": str(user.id),
        "status": "Active",
        "preferences": {"No Fish": True},
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/subscriptions", json=subscription_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["user_id"] == str(user.id)
    assert data["data"]["status"] == "Active"
    assert data["message"] == "Subscription created successfully"


def test_create_subscription_user_not_found(client: TestClient, db_session):
    """Test creating subscription for non-existent user."""
    fake_id = uuid4()
    
    subscription_data = {
        "user_id": str(fake_id),
        "status": "Active",
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/admin/subscriptions", json=subscription_data)
    
    assert response.status_code == 404


def test_update_subscription_success(client: TestClient, db_session):
    """Test updating a subscription successfully."""
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
    
    update_data = {
        "status": "Paused",
        "preferences": {"Updated": True}
    }
    
    response = client.patch(f"/api/v1/admin/subscriptions/{subscription.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["status"] == "Paused"
    assert data["data"]["preferences"] == {"Updated": True}
    assert data["message"] == "Subscription updated successfully"


def test_update_subscription_not_found(client: TestClient, db_session):
    """Test updating a subscription that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "status": "Paused"
    }
    
    response = client.patch(f"/api/v1/admin/subscriptions/{fake_id}", json=update_data)
    
    assert response.status_code == 404


def test_cancel_subscription_success(client: TestClient, db_session):
    """Test cancelling a subscription."""
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
    
    response = client.delete(f"/api/v1/admin/subscriptions/{subscription.id}")
    
    assert response.status_code == 204
    
    # Verify status was updated to Cancelled
    updated_subscription = subscription_repo.get(subscription.id)
    assert updated_subscription.status == "Cancelled"


def test_get_user_subscriptions(client: TestClient, db_session):
    """Test getting all subscriptions for a specific user."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create subscriptions for this user
    for i in range(3):
        subscription_repo.create(
            user_id=user.id,
            status="Active",
            started_at=datetime.now(timezone.utc)
        )
    
    response = client.get(f"/api/v1/admin/users/{user.id}/subscriptions")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["pagination"]["total"] == 3
    assert all(sub["user_id"] == str(user.id) for sub in data["data"])


def test_get_user_subscriptions_user_not_found(client: TestClient, db_session):
    """Test getting subscriptions for non-existent user."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/users/{fake_id}/subscriptions")
    
    assert response.status_code == 404


"""Tests for user subscriptions API endpoints."""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.subscription_repository import SubscriptionRepository
from app.core.repositories.user_repository import UserRepository


def test_get_subscriptions_empty(client: TestClient, db_session):
    """Test getting subscriptions when user has none."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    response = client.get(f"/api/v1/subscriptions?user_id={user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_get_subscriptions_with_pagination(client: TestClient, db_session):
    """Test getting subscriptions with pagination."""
    user_repo = UserRepository(db_session)
    subscription_repo = SubscriptionRepository(db_session)
    
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Create 5 subscriptions for this user
    for i in range(5):
        subscription_repo.create(
            user_id=user.id,
            status="Active",
            started_at=datetime.now(timezone.utc)
        )
    
    response = client.get(f"/api/v1/subscriptions?user_id={user.id}&skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5


def test_get_subscriptions_user_not_found(client: TestClient, db_session):
    """Test getting subscriptions for non-existent user."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/subscriptions?user_id={fake_id}")
    
    assert response.status_code == 404


def test_get_me_subscriptions_requires_auth(client: TestClient, db_session):
    """Test that /me/subscriptions requires authentication."""
    response = client.get("/api/v1/subscriptions/me/subscriptions")
    
    assert response.status_code == 501  # Not implemented without auth
    data = response.json()
    assert "authentication" in data["detail"].lower()


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
        "preferences": {"No Fish": True, "Vegetarian": True},
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/subscriptions", json=subscription_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["user_id"] == str(user.id)
    assert data["data"]["status"] == "Active"
    assert data["data"]["preferences"] == {"No Fish": True, "Vegetarian": True}
    assert data["message"] == "Subscription created successfully"


def test_create_subscription_invalid_status(client: TestClient, db_session):
    """Test creating a subscription with invalid status."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    subscription_data = {
        "user_id": str(user.id),
        "status": "InvalidStatus",
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/subscriptions", json=subscription_data)
    
    assert response.status_code == 422  # Validation error


def test_create_subscription_user_not_found(client: TestClient, db_session):
    """Test creating a subscription for non-existent user."""
    fake_id = uuid4()
    
    subscription_data = {
        "user_id": str(fake_id),
        "status": "Active",
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/subscriptions", json=subscription_data)
    
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
    
    response = client.get(f"/api/v1/subscriptions/{subscription.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(subscription.id)
    assert data["data"]["status"] == "Active"
    assert data["data"]["preferences"] == {"Vegan": True}


def test_get_subscription_not_found(client: TestClient, db_session):
    """Test getting a subscription that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/subscriptions/{fake_id}")
    
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
        preferences={"Old": True},
        started_at=datetime.now(timezone.utc)
    )
    
    update_data = {
        "status": "Paused",
        "preferences": {"New": True, "Updated": True}
    }
    
    response = client.patch(f"/api/v1/subscriptions/{subscription.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["status"] == "Paused"
    assert data["data"]["preferences"] == {"New": True, "Updated": True}
    assert data["message"] == "Subscription updated successfully"


def test_update_subscription_partial(client: TestClient, db_session):
    """Test partial update (only one field)."""
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
        "status": "Paused"
    }
    
    response = client.patch(f"/api/v1/subscriptions/{subscription.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["data"]["status"] == "Paused"
    # Other fields unchanged


def test_update_subscription_not_found(client: TestClient, db_session):
    """Test updating a subscription that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "status": "Paused"
    }
    
    response = client.patch(f"/api/v1/subscriptions/{fake_id}", json=update_data)
    
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
    
    response = client.delete(f"/api/v1/subscriptions/{subscription.id}")
    
    assert response.status_code == 204
    
    # Verify status was updated to Cancelled
    updated_subscription = subscription_repo.get(subscription.id)
    assert updated_subscription.status == "Cancelled"


def test_cancel_subscription_not_found(client: TestClient, db_session):
    """Test cancelling a subscription that doesn't exist."""
    fake_id = uuid4()
    
    response = client.delete(f"/api/v1/subscriptions/{fake_id}")
    
    assert response.status_code == 404


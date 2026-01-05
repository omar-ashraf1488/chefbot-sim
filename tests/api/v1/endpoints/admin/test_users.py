"""Tests for admin users API endpoints."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.repositories.user_repository import UserRepository


def test_list_users_empty(client: TestClient, db_session):
    """Test listing users when database is empty."""
    response = client.get("/api/v1/admin/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert data["data"] == []
    assert "pagination" in data
    assert data["pagination"]["skip"] == 0
    assert data["pagination"]["limit"] == 100
    assert data["pagination"]["total"] == 0


def test_list_users_with_pagination(client: TestClient, db_session):
    """Test listing users with pagination parameters."""
    user_repo = UserRepository(db_session)
    
    # Create 5 test users
    for i in range(5):
        user_repo.create(
            email=f"user{i}@example.com",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            timezone="UTC"
        )
    
    # Test with pagination
    response = client.get("/api/v1/admin/users?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["skip"] == 2
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["total"] == 5
    
    # Check user structure
    user = data["data"][0]
    assert "id" in user
    assert "email" in user
    assert "first_name" in user
    assert "last_name" in user
    assert "timezone" in user
    assert "created_at" in user
    assert "updated_at" in user


def test_get_user_success(client: TestClient, db_session):
    """Test getting a user by ID successfully."""
    user_repo = UserRepository(db_session)
    
    # Create a test user
    user = user_repo.create(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="America/New_York"
    )
    
    response = client.get(f"/api/v1/admin/users/{user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["id"] == str(user.id)
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["first_name"] == "Test"
    assert data["data"]["last_name"] == "User"
    assert data["data"]["timezone"] == "America/New_York"


def test_get_user_not_found(client: TestClient, db_session):
    """Test getting a user that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/users/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(fake_id) in data["detail"]


def test_create_user_success(client: TestClient, db_session):
    """Test creating a user successfully."""
    user_data = {
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/admin/users", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["email"] == user_data["email"]
    assert data["data"]["first_name"] == user_data["first_name"]
    assert data["data"]["last_name"] == user_data["last_name"]
    assert data["data"]["timezone"] == user_data["timezone"]
    assert "id" in data["data"]
    assert "created_at" in data["data"]
    assert "updated_at" in data["data"]
    assert data["message"] == "User created successfully"


def test_create_user_duplicate_email(client: TestClient, db_session):
    """Test creating a user with duplicate email."""
    user_repo = UserRepository(db_session)
    
    # Create a user first
    user_repo.create(
        email="existing@example.com",
        first_name="Existing",
        last_name="User",
        timezone="UTC"
    )
    
    # Try to create another user with same email
    user_data = {
        "email": "existing@example.com",
        "first_name": "New",
        "last_name": "User",
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/admin/users", json=user_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]


def test_create_user_invalid_timezone(client: TestClient, db_session):
    """Test creating a user with invalid timezone."""
    user_data = {
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "timezone": "Invalid/Timezone"
    }
    
    response = client.post("/api/v1/admin/users", json=user_data)
    
    assert response.status_code == 422  # Validation error
    data = response.json()
    assert "detail" in data


def test_update_user_success(client: TestClient, db_session):
    """Test updating a user successfully."""
    user_repo = UserRepository(db_session)
    
    # Create a user
    user = user_repo.create(
        email="original@example.com",
        first_name="Original",
        last_name="Name",
        timezone="UTC"
    )
    
    # Update the user
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    response = client.patch(f"/api/v1/admin/users/{user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert data["data"]["id"] == str(user.id)
    assert data["data"]["email"] == "original@example.com"  # Not updated
    assert data["data"]["first_name"] == "Updated"
    assert data["data"]["last_name"] == "Name"
    assert data["message"] == "User updated successfully"


def test_update_user_partial(client: TestClient, db_session):
    """Test partial update (only one field)."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="partial@example.com",
        first_name="Original",
        last_name="Original",
        timezone="UTC"
    )
    
    # Update only first_name
    update_data = {
        "first_name": "Changed"
    }
    
    response = client.patch(f"/api/v1/admin/users/{user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["data"]["first_name"] == "Changed"
    assert data["data"]["last_name"] == "Original"  # Unchanged
    assert data["data"]["email"] == "partial@example.com"  # Unchanged


def test_update_user_not_found(client: TestClient, db_session):
    """Test updating a user that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "first_name": "Updated"
    }
    
    response = client.patch(f"/api/v1/admin/users/{fake_id}", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_update_user_duplicate_email(client: TestClient, db_session):
    """Test updating user email to an existing email."""
    user_repo = UserRepository(db_session)
    
    # Create two users
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
    
    # Try to update user2's email to user1's email
    update_data = {
        "email": "user1@example.com"
    }
    
    response = client.patch(f"/api/v1/admin/users/{user2.id}", json=update_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]


def test_update_user_no_changes(client: TestClient, db_session):
    """Test updating a user with no fields (empty update)."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="nochange@example.com",
        first_name="Original",
        last_name="Name",
        timezone="UTC"
    )
    
    # Send empty update
    update_data = {}
    
    response = client.patch(f"/api/v1/admin/users/{user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["first_name"] == "Original"
    assert data["message"] == "No fields to update"


def test_update_user_same_email_allowed(client: TestClient, db_session):
    """Test that updating user with the same email is allowed."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="same@example.com",
        first_name="Original",
        last_name="Name",
        timezone="UTC"
    )
    
    # Update with same email but different name
    update_data = {
        "email": "same@example.com",  # Same email
        "first_name": "Updated"
    }
    
    response = client.patch(f"/api/v1/admin/users/{user.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == "same@example.com"
    assert data["data"]["first_name"] == "Updated"


def test_delete_user_success(client: TestClient, db_session):
    """Test deleting a user successfully (soft delete)."""
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        email="todelete@example.com",
        first_name="Delete",
        last_name="Me",
        timezone="UTC"
    )
    
    response = client.delete(f"/api/v1/admin/users/{user.id}")
    
    assert response.status_code == 204
    
    # Verify user is soft deleted (deleted_at is set)
    deleted_user = user_repo.get(user.id)
    assert deleted_user is not None
    assert deleted_user.deleted_at is not None


def test_delete_user_not_found(client: TestClient, db_session):
    """Test deleting a user that doesn't exist."""
    fake_id = uuid4()
    
    response = client.delete(f"/api/v1/admin/users/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_list_users_after_delete(client: TestClient, db_session):
    """Test that soft-deleted users are still counted (or verify behavior)."""
    user_repo = UserRepository(db_session)
    
    # Create users
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
    
    # Delete one user
    user_repo.soft_delete(user1.id)
    
    # List users - should still show both (soft delete, not filtered)
    response = client.get("/api/v1/admin/users")
    
    assert response.status_code == 200
    data = response.json()
    # Note: This behavior depends on your repository implementation
    # Currently get_all doesn't filter by deleted_at, so both will show
    assert data["pagination"]["total"] == 2


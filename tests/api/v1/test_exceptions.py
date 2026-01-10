"""Tests for exception handlers."""
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ConflictError


def test_not_found_error_handler(client: TestClient):
    """Test NotFoundError handler through FastAPI app."""
    # Test with a non-existent user
    response = client.get("/api/v1/users/me?user_id=00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["type"] == "NotFoundError"
    assert "not found" in data["error"]["message"].lower()


def test_conflict_error_handler(client: TestClient, db_session):
    """Test ConflictError handler through FastAPI app."""
    from app.core.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db_session)
    
    # Create a user
    user_repo.create(
        email="conflict@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    
    # Try to create another user with same email (should raise ConflictError)
    user_data = {
        "email": "conflict@example.com",
        "first_name": "Another",
        "last_name": "User",
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/admin/users", json=user_data)
    
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["type"] == "ConflictError"
    assert "already exists" in data["error"]["message"].lower() or "conflict" in data["error"]["message"].lower()


def test_integrity_error_handler(client: TestClient, db_session):
    """Test IntegrityError handler through repository."""
    from app.core.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db_session)
    
    # Create first user
    user_repo.create(
        email="integrity@example.com",
        first_name="First",
        last_name="User",
        timezone="UTC"
    )
    
    # Try to create duplicate - should raise ConflictError (converted from IntegrityError)
    with pytest.raises(ConflictError) as exc_info:
        user_repo.create(
            email="integrity@example.com",
            first_name="Second",
            last_name="User",
            timezone="UTC"
        )
    
    assert exc_info.value.status_code == 409
    assert "already exists" in str(exc_info.value.message).lower() or "conflict" in str(exc_info.value.message).lower()


def test_exception_handlers_integration(client: TestClient):
    """Test that exception handlers work through FastAPI app."""
    # Test endpoint that doesn't exist (404)
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    
    # Test endpoint that raises NotFoundError through users endpoint
    response = client.get("/api/v1/users/me?user_id=00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["success"] is False
    assert "NotFoundError" in response.json()["error"]["type"]
    assert "not found" in response.json()["error"]["message"].lower()

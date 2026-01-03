"""Unit tests for User Pydantic schemas."""
import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse


def test_user_create_valid():
    """Test creating a valid UserCreate schema."""
    user_data = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "timezone": "America/New_York"
    }
    user = UserCreate(**user_data)
    
    assert user.email == "test@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.timezone == "America/New_York"


def test_user_create_invalid_email():
    """Test that invalid email is rejected."""
    user_data = {
        "email": "not-an-email",
        "first_name": "John",
        "last_name": "Doe",
        "timezone": "UTC"
    }
    
    with pytest.raises(ValidationError):
        UserCreate(**user_data)


def test_user_create_invalid_timezone():
    """Test that invalid timezone is rejected."""
    user_data = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "timezone": "Invalid/Timezone"
    }
    
    with pytest.raises(ValidationError):
        UserCreate(**user_data)


def test_user_create_missing_fields():
    """Test that missing required fields are rejected."""
    user_data = {
        "email": "test@example.com"
        # Missing first_name, last_name, timezone
    }
    
    with pytest.raises(ValidationError):
        UserCreate(**user_data)


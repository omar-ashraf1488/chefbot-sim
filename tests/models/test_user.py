"""Unit tests for User model."""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User


def test_user_creation(db_session: Session):
    """Test creating a user in the database."""
    user = User(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.timezone == "UTC"
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.deleted_at is None


def test_user_email_unique(db_session: Session):
    """Test that email must be unique."""
    user1 = User(
        email="duplicate@example.com",
        first_name="First",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        email="duplicate@example.com",
        first_name="Second",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user2)
    
    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()


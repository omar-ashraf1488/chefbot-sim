"""Unit tests for Subscription model."""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.user import User


def test_subscription_creation(db_session: Session):
    """Test creating a subscription in the database."""
    # First create a user (required for foreign key)
    user = User(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a subscription
    subscription = Subscription(
        user_id=user.id,
        status="Active",
        preferences={"No Fish": True, "Vegan": False},
        started_at=datetime.now()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    assert subscription.id is not None
    assert subscription.user_id == user.id
    assert subscription.status == "Active"
    assert subscription.preferences == {"No Fish": True, "Vegan": False}
    assert subscription.started_at is not None
    assert subscription.created_at is not None
    assert subscription.updated_at is not None
    assert subscription.deleted_at is None


def test_subscription_status_values(db_session: Session):
    """Test creating subscriptions with all valid status values."""
    # Create a user
    user = User(
        email="status_test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Test all valid statuses
    valid_statuses = ["Active", "Paused", "Cancelled"]
    
    for status in valid_statuses:
        subscription = Subscription(
            user_id=user.id,
            status=status,
            started_at=datetime.now()
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        assert subscription.status == status
        assert subscription.id is not None


def test_subscription_preferences_nullable(db_session: Session):
    """Test that preferences can be None."""
    # Create a user
    user = User(
        email="nullable_prefs@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a subscription without preferences
    subscription = Subscription(
        user_id=user.id,
        status="Active",
        preferences=None,
        started_at=datetime.now()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    assert subscription.id is not None
    assert subscription.preferences is None
    assert subscription.status == "Active"


def test_subscription_preferences_json_formats(db_session: Session):
    """Test storing and retrieving different preference JSON formats."""
    # Create a user
    user = User(
        email="json_prefs@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Test different preference formats
    test_cases = [
        # Boolean values
        {"No Fish": True, "Vegan": False},
        # String values
        {"Dietary Restriction": "Gluten Free", "Allergy": "Peanuts"},
        # Mixed bool and str values
        {"No Fish": True, "Vegan": False, "Dietary Note": "Low Sodium"},
        # Empty dict
        {},
    ]
    
    for i, preferences in enumerate(test_cases):
        subscription = Subscription(
            user_id=user.id,
            status="Active",
            preferences=preferences,
            started_at=datetime.now()
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(subscription)
        
        assert subscription.id is not None
        assert subscription.preferences == preferences
        assert isinstance(subscription.preferences, dict)


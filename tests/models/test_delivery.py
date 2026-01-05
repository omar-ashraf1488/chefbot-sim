"""Unit tests for Delivery model."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.delivery import Delivery
from app.models.order import Order
from app.models.subscription import Subscription
from app.models.user import User


def test_delivery_creation(db_session: Session):
    """Test creating a delivery in the database."""
    # Create user, subscription, and order first
    user = User(
        email="delivery_test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    subscription = Subscription(
        user_id=user.id,
        status="Active",
        started_at=datetime.now()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    order = Order(
        subscription_id=subscription.id,
        recipes=[{"id": str(user.id), "name": "Pasta Carbonara"}],
        total_amount=Decimal("49.98"),
        status="shipped",
        order_date=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    
    # Create delivery
    delivery = Delivery(
        order_id=order.id,
        status="in_transit",
        expected_delivery_date=datetime.now(),
        actual_delivery_date=None,
        tracking_number="TRACK123456",
        notes="Left at front door"
    )
    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)
    
    assert delivery.id is not None
    assert delivery.order_id == order.id
    assert delivery.status == "in_transit"
    assert delivery.expected_delivery_date is not None
    assert delivery.actual_delivery_date is None
    assert delivery.tracking_number == "TRACK123456"
    assert delivery.notes == "Left at front door"
    assert delivery.created_at is not None
    assert delivery.updated_at is not None
    assert delivery.deleted_at is None


def test_delivery_status_values(db_session: Session):
    """Test creating deliveries with all valid status values."""
    # Create user, subscription, and order
    user = User(
        email="status_test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    subscription = Subscription(
        user_id=user.id,
        status="Active",
        started_at=datetime.now()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    # Test all valid statuses
    valid_statuses = ["delivered", "delayed", "failed", "in_transit"]
    
    for status in valid_statuses:
        order = Order(
            subscription_id=subscription.id,
            recipes=[{"id": str(user.id), "name": "Test Recipe"}],
            total_amount=Decimal("25.00"),
            status="shipped",
            order_date=datetime.now()
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        delivery = Delivery(
            order_id=order.id,
            status=status,
            expected_delivery_date=datetime.now()
        )
        db_session.add(delivery)
        db_session.commit()
        db_session.refresh(delivery)
        
        assert delivery.status == status
        assert delivery.id is not None


def test_delivery_nullable_fields(db_session: Session):
    """Test that nullable fields can be None."""
    # Create user, subscription, and order
    user = User(
        email="nullable_test@example.com",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    subscription = Subscription(
        user_id=user.id,
        status="Active",
        started_at=datetime.now()
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    
    order = Order(
        subscription_id=subscription.id,
        recipes=[{"id": str(user.id), "name": "Test Recipe"}],
        total_amount=Decimal("25.00"),
        status="shipped",
        order_date=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    
    # Create delivery with all nullable fields as None
    delivery = Delivery(
        order_id=order.id,
        status="in_transit",
        expected_delivery_date=datetime.now(),
        actual_delivery_date=None,
        tracking_number=None,
        notes=None
    )
    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)
    
    assert delivery.actual_delivery_date is None
    assert delivery.tracking_number is None
    assert delivery.notes is None


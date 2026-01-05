"""Unit tests for Order model."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.subscription import Subscription
from app.models.user import User


def test_order_creation(db_session: Session):
    """Test creating an order in the database."""
    # Create user and subscription first
    user = User(
        email="order_test@example.com",
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
    
    # Create order
    order = Order(
        subscription_id=subscription.id,
        recipes=[{"id": str(user.id), "name": "Pasta Carbonara"}],
        total_amount=Decimal("49.98"),
        status="pending",
        order_date=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    
    assert order.id is not None
    assert order.subscription_id == subscription.id
    assert order.recipes == [{"id": str(user.id), "name": "Pasta Carbonara"}]
    assert order.total_amount == Decimal("49.98")
    assert order.status == "pending"
    assert order.order_date is not None
    assert order.created_at is not None
    assert order.updated_at is not None
    assert order.deleted_at is None


def test_order_status_values(db_session: Session):
    """Test creating orders with all valid status values."""
    # Create user and subscription
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
    valid_statuses = ["pending", "shipped", "delivered", "cancelled"]
    
    for status in valid_statuses:
        order = Order(
            subscription_id=subscription.id,
            recipes=[{"id": str(user.id), "name": "Test Recipe"}],
            total_amount=Decimal("25.00"),
            status=status,
            order_date=datetime.now()
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        assert order.status == status
        assert order.id is not None


def test_order_recipes_json_formats(db_session: Session):
    """Test storing and retrieving different recipe JSON formats."""
    # Create user and subscription
    user = User(
        email="recipes_test@example.com",
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
    
    # Test different recipe formats
    test_cases = [
        [{"id": "uuid1", "name": "Recipe 1"}],
        [{"id": "uuid1", "name": "Recipe 1"}, {"id": "uuid2", "name": "Recipe 2"}],
        [{"id": "uuid1", "name": "Recipe 1", "quantity": 2}],
    ]
    
    for recipes in test_cases:
        order = Order(
            subscription_id=subscription.id,
            recipes=recipes,
            total_amount=Decimal("25.00"),
            status="pending",
            order_date=datetime.now()
        )
        db_session.add(order)
        db_session.commit()
        db_session.refresh(order)
        
        assert order.recipes == recipes
        assert isinstance(order.recipes, list)


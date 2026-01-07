"""Tests for UserRepository."""
import pytest
from sqlalchemy.orm import Session

from app.core.repositories.user_repository import UserRepository
from app.models.user import User


def test_create_user(db_session: Session):
    """Test creating a user through repository."""
    repo = UserRepository(db_session)
    user = repo.create(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        timezone="UTC"
    )
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.timezone == "UTC"
    assert user.created_at is not None


def test_get_user_by_id(db_session: Session):
    """Test getting a user by ID."""
    repo = UserRepository(db_session)
    created_user = repo.create(
        email="get@example.com",
        first_name="Jane",
        last_name="Smith",
        timezone="America/New_York"
    )
    
    found_user = repo.get(created_user.id)
    
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == "get@example.com"
    assert found_user.first_name == "Jane"


def test_get_user_not_found(db_session: Session):
    """Test getting a non-existent user returns None."""
    import uuid
    repo = UserRepository(db_session)
    non_existent_id = uuid.uuid4()
    
    found_user = repo.get(non_existent_id)
    
    assert found_user is None


def test_get_by_email(db_session: Session):
    """Test getting a user by email field."""
    repo = UserRepository(db_session)
    repo.create(
        email="find@example.com",
        first_name="Find",
        last_name="Me",
        timezone="UTC"
    )
    
    found_user = repo.get_by(email="find@example.com")
    
    assert found_user is not None
    assert found_user.email == "find@example.com"


def test_get_all_users(db_session: Session):
    """Test getting all users."""
    repo = UserRepository(db_session)
    repo.create(email="user1@example.com", first_name="User", last_name="One", timezone="UTC")
    repo.create(email="user2@example.com", first_name="User", last_name="Two", timezone="UTC")
    repo.create(email="user3@example.com", first_name="User", last_name="Three", timezone="UTC")
    
    users = repo.get_all()
    
    assert len(users) == 3
    assert all(isinstance(user, User) for user in users)


def test_get_all_with_pagination(db_session: Session):
    """Test getting users with pagination."""
    repo = UserRepository(db_session)
    for i in range(5):
        repo.create(
            email=f"user{i}@example.com",
            first_name="User",
            last_name=str(i),
            timezone="UTC"
        )
    
    # Get first 2
    users = repo.get_all(skip=0, limit=2)
    assert len(users) == 2
    
    # Skip first 2, get next 2
    users = repo.get_all(skip=2, limit=2)
    assert len(users) == 2


def test_update_user(db_session: Session):
    """Test updating a user."""
    repo = UserRepository(db_session)
    user = repo.create(
        email="update@example.com",
        first_name="Original",
        last_name="Name",
        timezone="UTC"
    )
    
    updated_user = repo.update(user.id, first_name="Updated", timezone="America/New_York")
    
    assert updated_user is not None
    assert updated_user.first_name == "Updated"
    assert updated_user.timezone == "America/New_York"
    assert updated_user.email == "update@example.com"  # Unchanged
    assert updated_user.last_name == "Name"  # Unchanged


def test_update_user_not_found(db_session: Session):
    """Test updating a non-existent user returns None."""
    import uuid
    repo = UserRepository(db_session)
    non_existent_id = uuid.uuid4()
    
    updated_user = repo.update(non_existent_id, first_name="Updated")
    
    assert updated_user is None


def test_delete_user(db_session: Session):
    """Test hard deleting a user."""
    repo = UserRepository(db_session)
    user = repo.create(
        email="delete@example.com",
        first_name="Delete",
        last_name="Me",
        timezone="UTC"
    )
    user_id = user.id
    
    result = repo.delete(user_id)
    
    assert result is True
    assert repo.get(user_id) is None


def test_delete_user_not_found(db_session: Session):
    """Test deleting a non-existent user returns False."""
    import uuid
    repo = UserRepository(db_session)
    non_existent_id = uuid.uuid4()
    
    result = repo.delete(non_existent_id)
    
    assert result is False


def test_soft_delete_user(db_session: Session):
    """Test soft deleting a user."""
    repo = UserRepository(db_session)
    user = repo.create(
        email="softdelete@example.com",
        first_name="Soft",
        last_name="Delete",
        timezone="UTC"
    )
    
    soft_deleted_user = repo.soft_delete(user.id)
    
    assert soft_deleted_user is not None
    assert soft_deleted_user.deleted_at is not None
    assert soft_deleted_user.id == user.id
    # User still exists in database (verify by querying directly)
    from sqlalchemy import select
    from app.models.user import User
    stmt = select(User).filter_by(id=user.id)
    found_user = db_session.scalar(stmt)
    assert found_user is not None
    assert found_user.deleted_at is not None
    # But get() should return None (soft-deleted records are filtered)
    assert repo.get(user.id) is None


def test_exists_user(db_session: Session):
    """Test checking if user exists."""
    repo = UserRepository(db_session)
    user = repo.create(
        email="exists@example.com",
        first_name="Exists",
        last_name="Check",
        timezone="UTC"
    )
    
    assert repo.exists(user.id) is True


def test_exists_user_not_found(db_session: Session):
    """Test checking if non-existent user exists."""
    import uuid
    repo = UserRepository(db_session)
    non_existent_id = uuid.uuid4()
    
    assert repo.exists(non_existent_id) is False


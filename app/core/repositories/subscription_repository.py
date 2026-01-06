"""Subscription repository for database operations."""
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.models.subscription import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription model operations."""
    
    def __init__(self, db: Session):
        """Initialize Subscription repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, Subscription)
    
    def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100):
        """Get all subscriptions for a specific user.
        
        Args:
            user_id: The UUID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of subscription instances for the user
        """
        stmt = (
            select(self.model)
            .filter_by(user_id=user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def count_by_user_id(self, user_id: UUID) -> int:
        """Count subscriptions for a specific user.
        
        Args:
            user_id: The UUID of the user
            
        Returns:
            Total count of subscriptions for the user
        """
        stmt = select(func.count(self.model.id)).filter_by(user_id=user_id)
        return self.db.scalar(stmt) or 0


"""Order repository for database operations."""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.models.order import Order


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model operations."""
    
    def __init__(self, db: Session):
        """Initialize Order repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, Order)
    
    def get_by_subscription_id(self, subscription_id: UUID, skip: int = 0, limit: int = 100):
        """Get all orders for a specific subscription.
        
        Args:
            subscription_id: The UUID of the subscription
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of order instances for the subscription
        """
        stmt = (
            select(self.model)
            .filter_by(subscription_id=subscription_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def count_by_subscription_id(self, subscription_id: UUID) -> int:
        """Count orders for a specific subscription.
        
        Args:
            subscription_id: The UUID of the subscription
            
        Returns:
            Total count of orders for the subscription
        """
        from sqlalchemy import func
        stmt = select(func.count(self.model.id)).filter_by(subscription_id=subscription_id)
        return self.db.scalar(stmt) or 0


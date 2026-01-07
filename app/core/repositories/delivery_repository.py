"""Delivery repository for database operations."""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.models.delivery import Delivery


class DeliveryRepository(BaseRepository[Delivery]):
    """Repository for Delivery model operations."""
    
    def __init__(self, db: Session):
        """Initialize Delivery repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, Delivery)
    
    def get_by_order_id(self, order_id: UUID):
        """Get delivery for a specific order.
        
        Args:
            order_id: The UUID of the order
            
        Returns:
            Delivery instance for the order, or None if not found
        """
        stmt = select(self.model).filter_by(order_id=order_id)
        return self.db.scalar(stmt)
    
    def count_by_order_id(self, order_id: UUID) -> int:
        """Count deliveries for a specific order.
        
        Args:
            order_id: The UUID of the order
            
        Returns:
            Total count of deliveries for the order (typically 0 or 1)
        """
        from sqlalchemy import func
        stmt = select(func.count(self.model.id)).filter_by(order_id=order_id)
        return self.db.scalar(stmt) or 0


"""Order model for tracking weekly meal kit boxes."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSON

from app.models.base import BaseModel


class Order(BaseModel):
    """Order model for tracking weekly meal kit boxes.
    
    Stores order information including subscription reference, recipes chosen,
    delivery date, and total amount. This is the primary table for tracking revenue.
    """
    
    __tablename__ = "orders"
    
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False, index=True)
    recipes = Column(JSON, nullable=False)  # JSON list: [{"id": "uuid", "name": "Recipe Name"}, ...]
    total_amount = Column(Numeric(10, 2), nullable=False)  # Total price for this order
    delivery_date = Column(DateTime(timezone=True), nullable=False, index=True)  # When the box is delivered
    status = Column(String, nullable=False, index=True)  # pending, shipped, delivered, cancelled
    order_date = Column(DateTime(timezone=True), nullable=False)  # When the order was placed


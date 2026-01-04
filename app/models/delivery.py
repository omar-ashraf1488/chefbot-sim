"""Delivery model for tracking meal kit box deliveries."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class Delivery(BaseModel):
    """Delivery model for tracking if meal kit boxes actually arrived.
    
    Tracks delivery status, dates, and notes to predict customer satisfaction
    and churn risk (e.g., if boxes are consistently late, food spoils).
    """
    
    __tablename__ = "deliveries"
    
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    status = Column(String, nullable=False, index=True)  # delivered, delayed, failed, in_transit
    expected_delivery_date = Column(DateTime(timezone=True), nullable=False)  # When the box should arrive
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)  # When the box actually arrived
    tracking_number = Column(String, nullable=True)  # Shipping tracking number
    notes = Column(Text, nullable=True)  # Additional delivery notes (e.g., "Left at front door", "Customer complaint")


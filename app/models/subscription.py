"""Subscription model for tracking meal kit subscriptions."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON

from app.models.base import BaseModel


class Subscription(BaseModel):
    """Subscription model for tracking meal kit subscriptions.
    
    Tracks subscription status (Active, Paused, Cancelled) and user preferences
    stored as JSON (e.g., "No Fish", "Vegan").
    """
    
    __tablename__ = "subscriptions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False, index=True)  # Active, Paused, Cancelled
    preferences = Column(JSON, nullable=True)  # JSON object for flexible preferences
    started_at = Column(DateTime(timezone=True), nullable=False)


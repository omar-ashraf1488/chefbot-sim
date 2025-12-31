"""Base model with common fields for all database tables."""
import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class BaseModel(Base):
    """Base model with common fields for all tables.
    
    Provides:
    - UUID primary key (auto-generated)
    - created_at timestamp (auto-populated)
    - updated_at timestamp (auto-updated on change)
    - deleted_at timestamp (for soft deletion)
    """
    
    __abstract__ = True  # Important: makes this a base class, not a table
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

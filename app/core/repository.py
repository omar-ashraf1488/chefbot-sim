"""Base repository for common database operations."""
from datetime import datetime
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations.
    
    This class provides a clean interface for database operations,
    automatically handling add, commit, and refresh operations.
    """
    
    def __init__(self, db: Session, model: Type[ModelType]):
        """Initialize repository with database session and model class.
        
        Args:
            db: SQLAlchemy database session
            model: The model class this repository handles
        """
        self.db = db
        self.model = model
    
    def create(self, **kwargs) -> ModelType:
        """Create a new model instance and save it to the database.
        
        Args:
            **kwargs: Model attributes to set
            
        Returns:
            The created and saved model instance
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """Get a model by ID.
        
        Args:
            id: The UUID of the model
            
        Returns:
            The model instance or None if not found
        """
        return self.db.get(self.model, id)
    
    def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get a single model by field values.
        
        Args:
            **kwargs: Field names and values to filter by
            
        Returns:
            The first matching model or None
        """
        stmt = select(self.model).filter_by(**kwargs)
        return self.db.scalar(stmt)
    
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        """Get all models with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional field filters
            
        Returns:
            List of model instances
        """
        stmt = select(self.model).filter_by(**filters).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())
    
    def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update a model by ID.
        
        Args:
            id: The UUID of the model to update
            **kwargs: Fields to update
            
        Returns:
            The updated model instance or None if not found
        """
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, id: UUID) -> bool:
        """Delete a model by ID (hard delete).
        
        Args:
            id: The UUID of the model to delete
            
        Returns:
            True if deleted, False if not found
        """
        instance = self.get(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
    
    def soft_delete(self, id: UUID) -> Optional[ModelType]:
        """Soft delete a model by setting deleted_at timestamp.
        
        Args:
            id: The UUID of the model to soft delete
            
        Returns:
            The updated model instance or None if not found
        """
        return self.update(id, deleted_at=datetime.utcnow())
    
    def exists(self, id: UUID) -> bool:
        """Check if a model exists by ID.
        
        Args:
            id: The UUID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.get(id) is not None
    
    def count(self, **filters) -> int:
        """Count total number of models matching filters.
        
        Args:
            **filters: Field filters to apply
            
        Returns:
            Total count of matching models
        """
        stmt = select(func.count(self.model.id)).filter_by(**filters)
        return self.db.scalar(stmt) or 0


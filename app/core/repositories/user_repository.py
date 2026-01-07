"""User repository for database operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        """Initialize User repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, User)
    
    def get_by_email(self, email: str):
        """Get user by email address (excludes soft-deleted records).
        
        Args:
            email: The email address to search for
            
        Returns:
            User instance if found, None otherwise
        """
        stmt = select(self.model).filter_by(email=email).filter(self.model.deleted_at.is_(None))
        return self.db.scalar(stmt)


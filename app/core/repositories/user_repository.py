"""User repository for database operations."""
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


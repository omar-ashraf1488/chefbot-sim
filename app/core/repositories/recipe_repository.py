"""Recipe repository for database operations."""
from sqlalchemy.orm import Session

from app.core.repository import BaseRepository
from app.models.recipe import Recipe


class RecipeRepository(BaseRepository[Recipe]):
    """Repository for Recipe model operations."""
    
    def __init__(self, db: Session):
        """Initialize Recipe repository.
        
        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, Recipe)


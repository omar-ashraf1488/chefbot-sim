"""User model for marketing data simulation."""
from sqlalchemy import Column, String

from app.models.base import BaseModel


class User(BaseModel):
    """User model for tracking marketing data.
    
    The id field (UUID) from BaseModel serves as the user_id.
    The created_at field from BaseModel serves as the signup_date.
    """
    
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    
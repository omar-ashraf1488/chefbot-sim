"""Recipe model for meal kit catalog."""
from sqlalchemy import Column, String, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import BaseModel


class Recipe(BaseModel):
    """Recipe model for storing meal kit catalog items.
    
    Stores recipe information including name, calories, tags, and other
    relevant details for marketing and ordering.
    """
    
    __tablename__ = "recipes"
    
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)  # Optional description of the recipe
    calories = Column(Integer, nullable=False, index=True)  # Calories per serving
    tags = Column(JSON, nullable=True)  # JSON array: ["Keto", "Family-Friendly", "Vegetarian"]
    price = Column(Numeric(10, 2), nullable=True)  # Price in currency (e.g., 24.99)
    preparation_time = Column(Integer, nullable=True)  # Preparation time in minutes
    servings = Column(Integer, nullable=True)  # Number of servings
    image_url = Column(String, nullable=True)  # URL to recipe image


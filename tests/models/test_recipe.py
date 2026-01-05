"""Unit tests for Recipe model."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.recipe import Recipe


def test_recipe_creation(db_session: Session):
    """Test creating a recipe in the database."""
    recipe = Recipe(
        name="Pasta Carbonara",
        description="Classic Italian pasta dish",
        calories=650,
        tags=["Italian", "Pasta", "Family-Friendly"],
        price=Decimal("24.99"),
        preparation_time=30,
        servings=4,
        image_url="https://example.com/carbonara.jpg"
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    
    assert recipe.id is not None
    assert recipe.name == "Pasta Carbonara"
    assert recipe.description == "Classic Italian pasta dish"
    assert recipe.calories == 650
    assert recipe.tags == ["Italian", "Pasta", "Family-Friendly"]
    assert recipe.price == Decimal("24.99")
    assert recipe.preparation_time == 30
    assert recipe.servings == 4
    assert recipe.image_url == "https://example.com/carbonara.jpg"
    assert recipe.created_at is not None
    assert recipe.updated_at is not None
    assert recipe.deleted_at is None


def test_recipe_minimal_required_fields(db_session: Session):
    """Test creating a recipe with only required fields."""
    recipe = Recipe(
        name="Simple Salad",
        calories=200
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    
    assert recipe.id is not None
    assert recipe.name == "Simple Salad"
    assert recipe.calories == 200
    assert recipe.description is None
    assert recipe.tags is None
    assert recipe.price is None
    assert recipe.preparation_time is None
    assert recipe.servings is None
    assert recipe.image_url is None


def test_recipe_tags_json_formats(db_session: Session):
    """Test storing and retrieving different tag formats."""
    test_cases = [
        ["Keto", "Low-Carb"],
        ["Vegetarian", "Vegan", "Gluten-Free"],
        [],  # Empty list
    ]
    
    for tags in test_cases:
        recipe = Recipe(
            name=f"Recipe with {len(tags)} tags",
            calories=300,
            tags=tags
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.tags == tags
        assert isinstance(recipe.tags, list)


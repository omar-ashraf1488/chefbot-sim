"""Unit tests for Recipe Pydantic schemas."""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.recipe import RecipeCreate, RecipeResponse


def test_recipe_create_valid():
    """Test creating a valid RecipeCreate schema."""
    recipe_data = {
        "name": "Pasta Carbonara",
        "description": "Classic Italian pasta dish",
        "calories": 650,
        "tags": ["Italian", "Pasta"],
        "price": Decimal("24.99"),
        "preparation_time": 30,
        "servings": 4,
        "image_url": "https://example.com/carbonara.jpg"
    }
    recipe = RecipeCreate(**recipe_data)
    
    assert recipe.name == "Pasta Carbonara"
    assert recipe.description == "Classic Italian pasta dish"
    assert recipe.calories == 650
    assert recipe.tags == ["Italian", "Pasta"]
    assert recipe.price == Decimal("24.99")
    assert recipe.preparation_time == 30
    assert recipe.servings == 4
    assert recipe.image_url == "https://example.com/carbonara.jpg"


def test_recipe_create_minimal_fields():
    """Test creating a recipe with only required fields."""
    recipe_data = {
        "name": "Simple Salad",
        "calories": 200
    }
    recipe = RecipeCreate(**recipe_data)
    
    assert recipe.name == "Simple Salad"
    assert recipe.calories == 200
    assert recipe.description is None
    assert recipe.tags is None
    assert recipe.price is None


def test_recipe_create_invalid_calories_negative():
    """Test that negative calories are rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": -100
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("calories",) for error in errors)


def test_recipe_create_invalid_price_negative():
    """Test that negative price is rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": 300,
        "price": Decimal("-10.00")
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("price",) for error in errors)


def test_recipe_create_invalid_preparation_time_zero():
    """Test that zero or negative preparation_time is rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": 300,
        "preparation_time": 0
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("preparation_time",) for error in errors)


def test_recipe_create_invalid_servings_zero():
    """Test that zero or negative servings is rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": 300,
        "servings": -1
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("servings",) for error in errors)


def test_recipe_create_invalid_tags_not_list():
    """Test that non-list tags are rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": 300,
        "tags": "not-a-list"
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("tags",) for error in errors)


def test_recipe_create_invalid_tags_not_strings():
    """Test that tags with non-string elements are rejected."""
    recipe_data = {
        "name": "Test Recipe",
        "calories": 300,
        "tags": ["Valid", 123, "Also Valid"]
    }
    
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreate(**recipe_data)
    
    errors = exc_info.value.errors()
    # Check if any error is related to tags (could be ("tags",) or ("tags", index))
    assert any("tags" in error["loc"] for error in errors)


def test_recipe_create_valid_tags_formats():
    """Test different valid tag formats."""
    test_cases = [
        ["Keto", "Low-Carb"],
        ["Vegetarian"],
        [],  # Empty list
    ]
    
    for tags in test_cases:
        recipe_data = {
            "name": "Test Recipe",
            "calories": 300,
            "tags": tags
        }
        recipe = RecipeCreate(**recipe_data)
        assert recipe.tags == tags


def test_recipe_create_missing_required_fields():
    """Test that missing required fields are rejected."""
    # Missing name
    with pytest.raises(ValidationError):
        RecipeCreate(calories=300)
    
    # Missing calories
    with pytest.raises(ValidationError):
        RecipeCreate(name="Test Recipe")


def test_recipe_response_valid():
    """Test creating a valid RecipeResponse schema."""
    recipe_data = {
        "id": uuid4(),
        "name": "Pasta Carbonara",
        "calories": 650,
        "tags": ["Italian"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    recipe = RecipeResponse(**recipe_data)
    
    assert recipe.id == recipe_data["id"]
    assert recipe.name == "Pasta Carbonara"
    assert recipe.calories == 650
    assert recipe.tags == ["Italian"]
    assert recipe.created_at is not None
    assert recipe.updated_at is not None


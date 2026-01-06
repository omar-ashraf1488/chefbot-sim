"""Tests for public recipes API endpoints."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from decimal import Decimal

from app.core.repositories.recipe_repository import RecipeRepository


def test_list_recipes_empty(client: TestClient, db_session):
    """Test listing recipes when database is empty."""
    response = client.get("/api/v1/recipes")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert data["data"] == []
    assert "pagination" in data
    assert data["pagination"]["skip"] == 0
    assert data["pagination"]["limit"] == 100
    assert data["pagination"]["total"] == 0


def test_list_recipes_with_pagination(client: TestClient, db_session):
    """Test listing recipes with pagination parameters."""
    recipe_repo = RecipeRepository(db_session)
    
    # Create 5 test recipes
    for i in range(5):
        recipe_repo.create(
            name=f"Recipe {i}",
            calories=300 + i * 50,
            tags=["Vegetarian"] if i % 2 == 0 else ["Keto"]
        )
    
    # Test with pagination
    response = client.get("/api/v1/recipes?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["skip"] == 2
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["total"] == 5
    
    # Check recipe structure
    recipe = data["data"][0]
    assert "id" in recipe
    assert "name" in recipe
    assert "calories" in recipe
    assert "created_at" in recipe
    assert "updated_at" in recipe


def test_get_recipe_success(client: TestClient, db_session):
    """Test getting a recipe by ID successfully."""
    recipe_repo = RecipeRepository(db_session)
    
    # Create a test recipe
    recipe = recipe_repo.create(
        name="Test Recipe",
        description="A delicious test recipe",
        calories=450,
        tags=["Vegetarian", "Family-Friendly"],
        price=Decimal("24.99"),
        preparation_time=30,
        servings=4,
        image_url="https://example.com/image.jpg"
    )
    
    response = client.get(f"/api/v1/recipes/{recipe.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check unified response structure
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["id"] == str(recipe.id)
    assert data["data"]["name"] == "Test Recipe"
    assert data["data"]["description"] == "A delicious test recipe"
    assert data["data"]["calories"] == 450
    assert data["data"]["tags"] == ["Vegetarian", "Family-Friendly"]
    assert float(data["data"]["price"]) == 24.99
    assert data["data"]["preparation_time"] == 30
    assert data["data"]["servings"] == 4
    assert data["data"]["image_url"] == "https://example.com/image.jpg"


def test_get_recipe_not_found(client: TestClient, db_session):
    """Test getting a recipe that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/recipes/{fake_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(fake_id) in data["detail"]


"""Tests for admin recipes API endpoints."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from decimal import Decimal

from app.core.repositories.recipe_repository import RecipeRepository


def test_list_recipes_empty(client: TestClient, db_session):
    """Test listing recipes when database is empty."""
    response = client.get("/api/v1/admin/recipes")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_list_recipes_with_pagination(client: TestClient, db_session):
    """Test listing recipes with pagination."""
    recipe_repo = RecipeRepository(db_session)
    
    for i in range(5):
        recipe_repo.create(
            name=f"Recipe {i}",
            calories=300 + i * 50
        )
    
    response = client.get("/api/v1/admin/recipes?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5


def test_get_recipe_success(client: TestClient, db_session):
    """Test getting a recipe by ID."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="Test Recipe",
        calories=450,
        tags=["Vegetarian"]
    )
    
    response = client.get(f"/api/v1/admin/recipes/{recipe.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["id"] == str(recipe.id)
    assert data["data"]["name"] == "Test Recipe"


def test_get_recipe_not_found(client: TestClient, db_session):
    """Test getting a recipe that doesn't exist."""
    fake_id = uuid4()
    
    response = client.get(f"/api/v1/admin/recipes/{fake_id}")
    
    assert response.status_code == 404


def test_create_recipe_success(client: TestClient, db_session):
    """Test creating a recipe successfully."""
    recipe_data = {
        "name": "New Recipe",
        "description": "A new recipe",
        "calories": 500,
        "tags": ["Keto", "Family-Friendly"],
        "price": "29.99",
        "preparation_time": 45,
        "servings": 6,
        "image_url": "https://example.com/image.jpg"
    }
    
    response = client.post("/api/v1/admin/recipes", json=recipe_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["name"] == recipe_data["name"]
    assert data["data"]["description"] == recipe_data["description"]
    assert data["data"]["calories"] == recipe_data["calories"]
    assert data["data"]["tags"] == recipe_data["tags"]
    assert float(data["data"]["price"]) == 29.99
    assert data["data"]["preparation_time"] == recipe_data["preparation_time"]
    assert data["data"]["servings"] == recipe_data["servings"]
    assert data["message"] == "Recipe created successfully"


def test_create_recipe_minimal(client: TestClient, db_session):
    """Test creating a recipe with only required fields."""
    recipe_data = {
        "name": "Simple Recipe",
        "calories": 300
    }
    
    response = client.post("/api/v1/admin/recipes", json=recipe_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["data"]["name"] == "Simple Recipe"
    assert data["data"]["calories"] == 300
    assert data["data"]["description"] is None


def test_create_recipe_invalid_calories(client: TestClient, db_session):
    """Test creating a recipe with negative calories."""
    recipe_data = {
        "name": "Invalid Recipe",
        "calories": -100
    }
    
    response = client.post("/api/v1/admin/recipes", json=recipe_data)
    
    assert response.status_code == 422  # Validation error


def test_create_recipe_invalid_price(client: TestClient, db_session):
    """Test creating a recipe with negative price."""
    recipe_data = {
        "name": "Invalid Recipe",
        "calories": 300,
        "price": "-10.00"
    }
    
    response = client.post("/api/v1/admin/recipes", json=recipe_data)
    
    assert response.status_code == 422  # Validation error


def test_update_recipe_success(client: TestClient, db_session):
    """Test updating a recipe successfully."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="Original Recipe",
        calories=400,
        description="Original description"
    )
    
    update_data = {
        "name": "Updated Recipe",
        "calories": 500
    }
    
    response = client.patch(f"/api/v1/admin/recipes/{recipe.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["data"]["name"] == "Updated Recipe"
    assert data["data"]["calories"] == 500
    assert data["data"]["description"] == "Original description"  # Not updated
    assert data["message"] == "Recipe updated successfully"


def test_update_recipe_partial(client: TestClient, db_session):
    """Test partial update (only one field)."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="Original",
        calories=300,
        price=Decimal("20.00")
    )
    
    update_data = {
        "name": "Changed"
    }
    
    response = client.patch(f"/api/v1/admin/recipes/{recipe.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["data"]["name"] == "Changed"
    assert data["data"]["calories"] == 300  # Unchanged
    assert float(data["data"]["price"]) == 20.00  # Unchanged


def test_update_recipe_not_found(client: TestClient, db_session):
    """Test updating a recipe that doesn't exist."""
    fake_id = uuid4()
    
    update_data = {
        "name": "Updated"
    }
    
    response = client.patch(f"/api/v1/admin/recipes/{fake_id}", json=update_data)
    
    assert response.status_code == 404


def test_update_recipe_no_changes(client: TestClient, db_session):
    """Test updating a recipe with no fields (empty update)."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="No Change",
        calories=300
    )
    
    update_data = {}
    
    response = client.patch(f"/api/v1/admin/recipes/{recipe.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "No Change"
    assert data["message"] == "No fields to update"


def test_update_recipe_tags(client: TestClient, db_session):
    """Test updating recipe tags."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="Tagged Recipe",
        calories=300,
        tags=["Vegetarian"]
    )
    
    update_data = {
        "tags": ["Keto", "Low-Carb"]
    }
    
    response = client.patch(f"/api/v1/admin/recipes/{recipe.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["tags"] == ["Keto", "Low-Carb"]


def test_delete_recipe_success(client: TestClient, db_session):
    """Test deleting a recipe successfully (soft delete)."""
    recipe_repo = RecipeRepository(db_session)
    
    recipe = recipe_repo.create(
        name="To Delete",
        calories=300
    )
    
    response = client.delete(f"/api/v1/admin/recipes/{recipe.id}")
    
    assert response.status_code == 204
    
    # Verify recipe is soft deleted
    deleted_recipe = recipe_repo.get(recipe.id)
    assert deleted_recipe is not None
    assert deleted_recipe.deleted_at is not None


def test_delete_recipe_not_found(client: TestClient, db_session):
    """Test deleting a recipe that doesn't exist."""
    fake_id = uuid4()
    
    response = client.delete(f"/api/v1/admin/recipes/{fake_id}")
    
    assert response.status_code == 404


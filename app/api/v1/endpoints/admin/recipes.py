"""Admin recipes API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.recipe_repository import RecipeRepository
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[RecipeResponse], status_code=200)
def list_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """List all recipes with pagination.
    
    Admin-only endpoint. Returns paginated list of all recipes.
    Note: In production, this would require admin authentication/authorization.
    """
    recipe_repo = RecipeRepository(db)
    recipes = recipe_repo.get_all(skip=skip, limit=limit)
    total = recipe_repo.count()
    
    recipe_responses = [RecipeResponse.model_validate(recipe) for recipe in recipes]
    
    return PaginatedResponse(
        success=True,
        data=recipe_responses,
        pagination=PaginationMeta(skip=skip, limit=limit, total=total)
    )


@router.get("/{recipe_id}", response_model=Response[RecipeResponse], status_code=200)
def get_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a recipe by ID.
    
    Admin-only endpoint. Returns recipe details by ID.
    Note: In production, this would require admin authentication/authorization.
    """
    recipe_repo = RecipeRepository(db)
    recipe = recipe_repo.get(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    
    return Response(
        success=True,
        data=RecipeResponse.model_validate(recipe)
    )


@router.post("", response_model=Response[RecipeResponse], status_code=201)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
):
    """Create a new recipe.
    
    Admin-only endpoint. Creates a new recipe in the catalog.
    Note: In production, this would require admin authentication/authorization.
    """
    recipe_repo = RecipeRepository(db)
    
    recipe = recipe_repo.create(**recipe_data.model_dump())
    
    return Response(
        success=True,
        data=RecipeResponse.model_validate(recipe),
        message="Recipe created successfully"
    )


@router.patch("/{recipe_id}", response_model=Response[RecipeResponse], status_code=200)
def update_recipe(
    recipe_id: UUID,
    recipe_data: RecipeUpdate,
    db: Session = Depends(get_db),
):
    """Update a recipe by ID.
    
    Admin-only endpoint. Updates recipe fields (partial update).
    Note: In production, this would require admin authentication/authorization.
    """
    recipe_repo = RecipeRepository(db)
    
    # Check if recipe exists
    recipe = recipe_repo.get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    
    # Prepare update data (only include non-None fields)
    update_data = {k: v for k, v in recipe_data.model_dump().items() if v is not None}
    
    if not update_data:
        # No fields to update
        return Response(
            success=True,
            data=RecipeResponse.model_validate(recipe),
            message="No fields to update"
        )
    
    updated_recipe = recipe_repo.update(recipe_id, **update_data)
    
    return Response(
        success=True,
        data=RecipeResponse.model_validate(updated_recipe),
        message="Recipe updated successfully"
    )


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a recipe by ID (soft delete).
    
    Admin-only endpoint. Soft deletes a recipe by setting deleted_at timestamp.
    Note: In production, this would require admin authentication/authorization.
    """
    recipe_repo = RecipeRepository(db)
    
    # Check if recipe exists
    recipe = recipe_repo.get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    
    recipe_repo.soft_delete(recipe_id)
    return None


"""Public recipes API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.schemas import PaginatedResponse, PaginationMeta, Response
from app.core.db import get_db
from app.core.repositories.recipe_repository import RecipeRepository
from app.schemas.recipe import RecipeResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[RecipeResponse], status_code=200)
def list_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """List recipes with pagination.
    
    Public endpoint. Returns paginated list of all recipes (catalog).
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
    
    Public endpoint. Returns recipe details by ID.
    """
    recipe_repo = RecipeRepository(db)
    recipe = recipe_repo.get(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
    
    return Response(
        success=True,
        data=RecipeResponse.model_validate(recipe)
    )


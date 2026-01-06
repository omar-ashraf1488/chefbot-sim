"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import recipes
from app.api.v1.endpoints.admin import admin_router

api_router = APIRouter()

# Public endpoints
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])

# Admin endpoints group
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])


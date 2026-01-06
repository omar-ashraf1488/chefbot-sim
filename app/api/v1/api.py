"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import recipes, subscriptions
from app.api.v1.endpoints.admin import admin_router

api_router = APIRouter()

# Public/User endpoints
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])

# Admin endpoints group
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])


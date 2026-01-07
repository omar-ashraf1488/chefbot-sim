"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import deliveries, orders, recipes, subscriptions, users
from app.api.v1.endpoints.admin import admin_router

api_router = APIRouter()

# Public/User endpoints
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Admin endpoints group
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])


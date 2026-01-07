"""Admin API endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints.admin import orders, recipes, subscriptions, users

# Create admin router
admin_router = APIRouter()

# Include all admin endpoint routers
admin_router.include_router(users.router, prefix="/users", tags=["admin-users"])
admin_router.include_router(recipes.router, prefix="/recipes", tags=["admin-recipes"])
admin_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["admin-subscriptions"])
admin_router.include_router(orders.router, prefix="/orders", tags=["admin-orders"])

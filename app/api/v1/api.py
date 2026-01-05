"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints.admin import users as admin_users

api_router = APIRouter()

# Admin endpoints
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin-users"])


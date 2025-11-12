"""
API V1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, credits, jobs, subscriptions

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(credits.router, prefix="/credits", tags=["Credits"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])

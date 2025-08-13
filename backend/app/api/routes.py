"""
API routes for CybeMeeting
"""
from fastapi import APIRouter
from app.api.endpoints import projects, meetings, auth

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])

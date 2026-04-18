"""
LoveAdvisor V3 - API Package
Phase 1: Engineering Skeleton Initialization

This package contains all FastAPI routes and endpoints for the LoveAdvisor V3 system.
"""

from app.api.analyze import router as analyze_router
from app.api.health import router as health_router
from app.api.debug import router as debug_router
from app.api.history import router as history_router

__all__ = [
    "analyze_router",
    "health_router",
    "debug_router",
    "history_router",
]
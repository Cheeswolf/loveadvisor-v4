"""
LoveAdvisor V3 - FastAPI Application Entry Point
Phase 1: Engineering Skeleton Initialization

This module initializes the FastAPI application and configures middleware, routes,
and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.api.health import router as health_router
from app.api.debug import router as debug_router
from app.api.image_to_text import router as image_to_text_router
from app.api.history import router as history_router


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="LoveAdvisor V3 API",
        description="AI-powered emotional analysis and relationship decision assistant",
        version="3.0.0-alpha",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict to frontend domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(analyze_router, prefix="/api/v1", tags=["analysis"])
    app.include_router(debug_router, prefix="/api/v1", tags=["debug"])
    app.include_router(image_to_text_router, prefix="/api/v1", tags=["image-to-text"])
    app.include_router(history_router, prefix="/api/v1", tags=["history"])

    # Startup event: initialize runtime context and services
    @app.on_event("startup")
    async def startup_event():
        """
        Initialize application services on startup.

        TODO: Initialize runtime context, load configurations, warm up caches.
        """
        pass

    # Shutdown event: clean up resources
    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Clean up application resources on shutdown.

        TODO: Clean up LLM connections, close database sessions, etc.
        """
        pass

    return app


# Global application instance
app = create_app()
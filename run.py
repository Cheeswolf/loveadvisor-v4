"""
LoveAdvisor V3 - Application Runner
Phase 1: Engineering Skeleton Initialization

This script serves as the entry point to run the LoveAdvisor V3 application.
It starts the FastAPI server with configuration from settings.
"""

import uvicorn
from app.main import app
from configs.settings import HOST, PORT, DEBUG


if __name__ == "__main__":
    """
    Run the FastAPI application using uvicorn.

    Configuration is loaded from configs.settings.
    """
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )
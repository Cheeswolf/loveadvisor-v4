"""
LoveAdvisor V4 - Image to Text API Endpoint (I1)
Phase 1: Standard Three-Layer Architecture Implementation

This module defines the I1 image-to-text endpoint following V4 architecture:
- API layer: routing, request handling, response formatting
- Service layer: business logic (delegated to image_to_text_service)
- Schema layer: request/response models (defined in schemas)

The endpoint receives uploaded images and returns mock text extraction results
following the I1 protocol specification.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.image_to_text_models import ImageToTextResponse
from app.services.image_to_text_service import image_to_text


router = APIRouter()


@router.post("/image-to-text", response_model=ImageToTextResponse)
async def image_to_text_endpoint(
    images: List[UploadFile] = File(..., description="Images to process (1-10 files)"),
    provider: str = "qwen_ocr",
    source_type: str = "image",
    request_id: Optional[str] = None
) -> ImageToTextResponse:
    """
    Convert uploaded images to text using I1 protocol with mock providers.

    This endpoint accepts multiple image uploads and processes them using mock
    providers following the V4 three-layer architecture:
    1. API layer (this function): handles routing and request/response formatting
    2. Service layer (image_to_text_service): implements business logic
    3. Schema layer (image_to_text_models): defines request/response models

    Args:
        images: List of image files to process (JPEG, PNG, GIF, BMP, WebP)
        provider: Text extraction provider (default: "qwen_ocr")
        source_type: Source type identifier (default: "image")
        request_id: Optional request ID for tracking

    Returns:
        ImageToTextResponse following I1 protocol specification with mock data

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        # Call the image_to_text service with single provider implementation
        return await image_to_text(
            images=images,
            provider=provider,
            source_type=source_type,
            request_id=request_id
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors with structured response
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Image-to-text processing failed: {e}", exc_info=True)

        # Return error response instead of raising HTTPException to maintain consistent format
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            provider=provider,
            source_type=source_type,
            image_count=len(images) if 'images' in locals() else 0,
            need_user_confirm=True,
            error_message=f"Internal server error: {str(e)}",
            request_id=request_id or str(uuid.uuid4()),
            metadata={
                "api_version": "v1",
                "error": True,
                "error_type": "unexpected_exception"
            }
        )
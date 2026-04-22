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
        # DEBUG: Log provider and request info
        import os
        debug_file = os.path.expanduser('~/debug_endpoint.txt')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f'provider={provider}\n')
            f.write(f'request_id={request_id}\n')
            f.write(f'image_count={len(images)}\n')
        print(f"[DEBUG] image_to_text_endpoint: provider={provider}, request_id={request_id}, image_count={len(images)}")
        # Call the image_to_text service with single provider implementation
        response = await image_to_text(
            images=images,
            provider=provider,
            source_type=source_type,
            request_id=request_id
        )
        # DEBUG: Log final response before returning
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[ROUTE DEBUG] Final response before returning: success={response.success}, provider={response.provider}, error_message={response.error_message}, metadata.implementation={response.metadata.get('implementation', 'N/A')}, raw_text preview={response.raw_text[:50] if response.raw_text else ''}")
        # Also write to file for debugging
        with open('debug_route_final.txt', 'w', encoding='utf-8') as f:
            f.write(f"success={response.success}\n")
            f.write(f"provider={response.provider}\n")
            f.write(f"error_message={response.error_message}\n")
            f.write(f"metadata.implementation={response.metadata.get('implementation', 'N/A')}\n")
            f.write(f"raw_text preview={response.raw_text[:50] if response.raw_text else ''}\n")
            f.write(f"full response model: {response}\n")
        print(f"[ROUTE DEBUG] Final response: success={response.success}, provider={response.provider}")
        return response

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
        error_response = ImageToTextResponse(
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
        # DEBUG: Log error response before returning
        logger.info(f"[ROUTE DEBUG] Error response before returning: success={error_response.success}, provider={error_response.provider}, error_message={error_response.error_message}, metadata.implementation={error_response.metadata.get('implementation', 'N/A')}, raw_text preview={error_response.raw_text[:50] if error_response.raw_text else ''}")
        with open('debug_route_error.txt', 'w', encoding='utf-8') as f:
            f.write(f"success={error_response.success}\n")
            f.write(f"provider={error_response.provider}\n")
            f.write(f"error_message={error_response.error_message}\n")
            f.write(f"metadata.implementation={error_response.metadata.get('implementation', 'N/A')}\n")
            f.write(f"raw_text preview={error_response.raw_text[:50] if error_response.raw_text else ''}\n")
        print(f"[ROUTE DEBUG] Error response: success={error_response.success}, provider={error_response.provider}")
        return error_response
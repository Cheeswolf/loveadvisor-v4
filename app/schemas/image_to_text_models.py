"""
LoveAdvisor V4 - Image to Text Models (I1)
Phase 1: Standard Three-Layer Architecture Implementation

This module contains Pydantic models for the I1 image-to-text API endpoint.
These models define the request and response structures according to the frozen I1 protocol
and support the V4 standard three-layer architecture (API + Schema + Service).
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ImageToTextRequest(BaseModel):
    """
    Request model for the I1 image-to-text endpoint.

    Following the frozen I1 protocol, images are provided as a list of strings
    (base64-encoded data or file references). The actual implementation may use
    multipart file uploads for better performance with large images.
    """
    images: List[str] = Field(
        ...,
        description="List of image data (base64-encoded strings or file references)"
    )


class ImageToTextResponse(BaseModel):
    """
    Response model for the I1 image-to-text endpoint.

    This model follows the frozen I1 protocol specification exactly.
    All fields must be present in the response as defined in the protocol.
    """
    success: bool = Field(..., description="Whether processing succeeded")
    raw_text: str = Field(..., description="Raw text extracted from all images (concatenated string)")
    merged_text: str = Field(..., description="Combined text from all images")
    provider: str = Field(..., description="Provider used for extraction")
    source_type: str = Field(..., description="Source type identifier, must be 'image'")
    image_count: int = Field(..., description="Number of images processed")
    need_user_confirm: bool = Field(
        default=True,
        description="Whether user confirmation is needed for accuracy (always true per I1 protocol)"
    )
    error_message: str = Field(
        default="",
        description="Error message if processing failed"
    )

    # Optional fields for tracking and extensibility
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for tracking (echoed from request or generated)"
    )
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )


# Alias for backward compatibility
ImageToTextRequestModel = ImageToTextRequest
ImageToTextResponseModel = ImageToTextResponse


class ImageToTextQueryParams(BaseModel):
    """
    Query parameters for the image-to-text endpoint.

    These parameters are passed as form data or query parameters alongside file uploads.
    """
    provider: str = Field(
        default="qwen_ocr",
        description="Text extraction provider (qwen_ocr or vision_model_v1)"
    )
    source_type: str = Field(
        default="image",
        description="Source type identifier (default: 'image')"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Optional request ID for tracking"
    )
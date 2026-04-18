"""
LoveAdvisor V4 - Image to Text Service (I1) Mock
Phase 1: Empty Interface Implementation

This module provides a mock service layer for converting images to text (I1 protocol).
Returns placeholder text without calling any real OCR providers.
"""

import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile

from app.schemas.image_to_text_models import ImageToTextResponse


async def mock_qwen_ocr_extract(image: UploadFile) -> Tuple[bool, str, str]:
    """
    Mock extraction using Qwen-OCR provider.

    Returns a placeholder text for demonstration.
    """
    # Simulate successful extraction with mock text
    mock_text = (
        "这是从图片中提取的模拟文本。\n"
        "用户A: 你好，最近怎么样？\n"
        "用户B: 还不错，谢谢关心。\n"
        "实际使用时会调用真实的Qwen-OCR API。"
    )
    return True, mock_text, ""


async def mock_vision_model_v1_extract(image: UploadFile) -> Tuple[bool, str, str]:
    """
    Mock extraction using vision_model_v1 provider.

    Returns a placeholder text for demonstration.
    """
    # Simulate successful extraction with mock text
    mock_text = (
        "这是vision_model_v1提供的模拟文本。\n"
        "图片内容：聊天记录截图\n"
        "文本已提取，等待进一步处理。"
    )
    return True, mock_text, ""


async def image_to_text(
    images: List[UploadFile],
    provider: str = "qwen_ocr",
    source_type: str = "image",
    request_id: Optional[str] = None
) -> ImageToTextResponse:
    """
    Convert uploaded images to text using mock providers.

    This function implements a mock image-to-text processing pipeline:
    1. Receive image list
    2. Validate count and basic types
    3. Process each image with mock provider
    4. Concatenate raw_text
    5. Generate merged_text and return unified result

    Error handling strategy (conservative):
    - E1: No images received → overall failure
    - E2: Recognition failure → overall failure (not used in mock)
    - E3: No valid text detected → overall failure (not used in mock)
    - E4: Any single image fails → overall failure (not used in mock)

    Args:
        images: List of uploaded image files
        provider: Text extraction provider (default: "qwen_ocr")
        source_type: Source type identifier (default: "image")
        request_id: Optional request ID for tracking

    Returns:
        ImageToTextResponse following I1 protocol specification with mock data
    """
    # Generate request ID if not provided
    request_id = request_id or str(uuid.uuid4())

    # ------------------------------------------------------------------------
    # Step 1: Basic validation
    # ------------------------------------------------------------------------

    # E1: No images received
    if not images:
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            provider=provider,
            source_type=source_type,
            image_count=0,
            need_user_confirm=True,
            error_message="未收到图片",
            request_id=request_id,
            metadata={"error_type": "E1_no_images"}
        )

    # Check maximum number of images (configurable)
    max_images = 10
    if len(images) > max_images:
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            provider=provider,
            source_type=source_type,
            image_count=len(images),
            need_user_confirm=True,
            error_message=f"Maximum {max_images} images allowed",
            request_id=request_id,
            metadata={"error_type": "validation_failed", "max_images": max_images}
        )

    # Check file types
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    for image in images:
        if image.filename:
            filename_lower = image.filename.lower()
            if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
                return ImageToTextResponse(
                    success=False,
                    raw_text="",
                    merged_text="",
                    provider=provider,
                    source_type=source_type,
                    image_count=len(images),
                    need_user_confirm=True,
                    error_message=f"Unsupported file type: {image.filename}. Allowed: {', '.join(allowed_extensions)}",
                    request_id=request_id,
                    metadata={"error_type": "validation_failed", "unsupported_file": image.filename}
                )

    # ------------------------------------------------------------------------
    # Step 2: Process images with mock provider
    # ------------------------------------------------------------------------

    raw_text_parts = []
    all_successful = True
    error_message = ""

    for i, image in enumerate(images):
        # Call mock provider for each image
        if provider == "qwen_ocr":
            success, extracted_text, error_msg = await mock_qwen_ocr_extract(image)
        elif provider == "vision_model_v1":
            success, extracted_text, error_msg = await mock_vision_model_v1_extract(image)
        else:
            # Only qwen_ocr and vision_model_v1 are supported in this implementation
            success, extracted_text, error_msg = False, "", f"Unsupported provider: {provider}"

        if not success:
            # E4: Any single image fails → overall failure (conservative strategy)
            all_successful = False
            error_message = error_msg
            break

        # Add image separator and extracted text
        raw_text_parts.append(f"[Image {i+1}]\n{extracted_text.strip()}")

    # ------------------------------------------------------------------------
    # Step 3: Handle failures
    # ------------------------------------------------------------------------

    if not all_successful:
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            provider=provider,
            source_type=source_type,
            image_count=len(images),
            need_user_confirm=True,
            error_message=error_message,
            request_id=request_id,
            metadata={
                "error_type": "extraction_failed",
                "provider": provider,
                "images_processed": i if not all_successful else len(images)
            }
        )

    # ------------------------------------------------------------------------
    # Step 4: Generate raw_text and merged_text
    # ------------------------------------------------------------------------

    # raw_text: concatenated raw extraction results with image separators
    raw_text = "\n\n".join(raw_text_parts)

    # merged_text: simple strip as per V3.6 MTU-1 requirements
    merged_text = raw_text.strip()

    # ------------------------------------------------------------------------
    # Step 5: Return successful response
    # ------------------------------------------------------------------------

    return ImageToTextResponse(
        success=True,
        raw_text=raw_text,
        merged_text=merged_text,
        provider=provider,
        source_type=source_type,
        image_count=len(images),
        need_user_confirm=True,  # Always True per I1 protocol
        error_message="",
        request_id=request_id,
        metadata={
            "api_version": "v1",
            "endpoint": "image-to-text",
            "provider_used": provider,
            "images_processed": len(images),
            "implementation": "mock_provider"
        }
    )
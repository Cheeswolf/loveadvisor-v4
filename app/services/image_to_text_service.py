"""
LoveAdvisor V4 - Image to Text Service (I1) Mock
Phase 1: Empty Interface Implementation

This module provides a mock service layer for converting images to text (I1 protocol).
Returns placeholder text without calling any real OCR providers.
"""

import asyncio
import base64
import copy
import io
import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile
import httpx
from configs import settings

from app.schemas.image_to_text_models import ImageToTextResponse

import sys
import datetime

def debug_log(msg):
    """Write debug message to file and stdout."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg, file=sys.stderr, flush=True)
    try:
        with open('debug_image_service.log', 'a', encoding='utf-8') as f:
            f.write(full_msg + '\n')
    except Exception:
        pass


async def real_qwen_ocr_extract(image: UploadFile) -> Tuple[bool, str, str]:
    """
    Real extraction using Qwen-OCR provider via DashScope API.

    Returns extracted text from image.
    """
    debug_log(f"[DEBUG] real_qwen_ocr_extract called for file: {image.filename}")
    # Read image content
    content = await image.read()
    # Reset file pointer for potential reuse
    await image.seek(0)

    # Encode image to base64
    image_b64 = base64.b64encode(content).decode('utf-8')
    # Determine MIME type from filename or default
    if image.filename and image.filename.lower().endswith(('.png',)):
        mime_type = 'image/png'
    elif image.filename and image.filename.lower().endswith(('.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    elif image.filename and image.filename.lower().endswith(('.gif',)):
        mime_type = 'image/gif'
    elif image.filename and image.filename.lower().endswith(('.bmp',)):
        mime_type = 'image/bmp'
    elif image.filename and image.filename.lower().endswith(('.webp',)):
        mime_type = 'image/webp'
    else:
        mime_type = 'image/jpeg'  # default

    # Prepare request payload according to DashScope compatible mode
    payload = {
        "model": settings.QWEN_OCR_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请提取图片中的聊天文本，按阅读顺序输出为带有说话人区分与轮次结构的聊天草稿。\n\n要求：\n1. 优先恢复聊天轮次，按时间顺序排列\n2. 优先区分双方说话人，如果无法高置信度恢复具体身份，使用中性标签：A: 和 B:\n3. 保留主要文本内容，去掉明显系统噪声（如时间戳、系统提示、无意义UI文本）\n4. 若部分轮次无法判断归属，也要尽量按轮次分行，而不是全部糊成一段\n5. 不要编造不存在的内容\n6. 不要输出解释文字\n7. 输出必须是纯聊天草稿格式，例如：\nA: 你好\nB: 你好啊\nA: 最近怎么样？\n\n或\n我: 在干嘛？\n对方: 刚下班\n\n请直接输出聊天草稿，不要其他文字。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Debug logging of request details
    debug_log(f"[DEBUG] QWEN_OCR_BASE_URL: {settings.QWEN_OCR_BASE_URL}")
    debug_log(f"[DEBUG] QWEN_OCR_MODEL: {settings.QWEN_OCR_MODEL}")
    debug_log(f"[DEBUG] Authorization header present: {'Yes' if settings.DASHSCOPE_API_KEY else 'No'}")
    debug_log(f"[DEBUG] Payload model: {payload.get('model')}")
    debug_log(f"[DEBUG] Messages structure: {payload.get('messages')}")
    # Log payload without image base64 to avoid huge logs
    import copy
    payload_copy = copy.deepcopy(payload)
    if 'messages' in payload_copy and len(payload_copy['messages']) > 0:
        content = payload_copy['messages'][0].get('content', [])
        for item in content:
            if item.get('type') == 'image_url':
                item['image_url']['url'] = 'data:image/...base64... (truncated)'
    debug_log(f"[DEBUG] Payload (truncated): {payload_copy}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.QWEN_OCR_BASE_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()

            # Extract text from response
            # The response structure may vary; typical DashScope response has choices[0].message.content
            if 'choices' in result and len(result['choices']) > 0:
                extracted_text = result['choices'][0]['message']['content']
            elif 'output' in result and 'text' in result['output']:
                extracted_text = result['output']['text']
            elif 'text' in result:
                extracted_text = result['text']
            else:
                # Fallback: try to find any text field
                extracted_text = str(result).strip()
                if not extracted_text or extracted_text == '{}':
                    extracted_text = ""

            if not extracted_text:
                return False, "", "未识别到文字"

            debug_log(f"[DEBUG] real_qwen_ocr_extract succeeded, extracted_text length: {len(extracted_text)}")
            return True, extracted_text, ""

    except httpx.HTTPStatusError as e:
        debug_log(f"[DEBUG] real_qwen_ocr_extract HTTPStatusError: {e.response.status_code} {e.response.text}")
        error_msg = f"API请求失败: {e.response.status_code} {e.response.text}"
        return False, "", error_msg
    except httpx.RequestError as e:
        debug_log(f"[DEBUG] real_qwen_ocr_extract RequestError: {str(e)}")
        error_msg = f"网络请求失败: {str(e)}"
        return False, "", error_msg
    except Exception as e:
        debug_log(f"[DEBUG] real_qwen_ocr_extract Exception: {str(e)}")
        error_msg = f"处理失败: {str(e)}"
        return False, "", error_msg


async def mock_qwen_ocr_extract(image: UploadFile) -> Tuple[bool, str, str]:
    """
    Mock extraction using Qwen-OCR provider.

    Returns a placeholder text for demonstration.
    """
    debug_log(f"[DEBUG] mock_qwen_ocr_extract called for file: {image.filename}")
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
    debug_log(f"[DEBUG] mock_vision_model_v1_extract called for file: {image.filename}")
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

    # DEBUG: Log provider and request info
    import sys, os
    debug_file = os.path.expanduser('~/debug_image_to_text.txt')
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(f'provider={provider}\n')
        f.write(f'source_type={source_type}\n')
        f.write(f'request_id={request_id}\n')
        f.write(f'image_count={len(images)}\n')
    print(f"[DIRECT PRINT] image_to_text service: provider={provider}", file=sys.stderr, flush=True)
    debug_log(f"[DEBUG] image_to_text service: provider={provider}, source_type={source_type}, request_id={request_id}, image_count={len(images)}")
    # Write provider to file for debugging
    try:
        with open('debug_provider.txt', 'w', encoding='utf-8') as f:
            f.write(f"provider={provider}\n")
    except Exception as e:
        debug_log(f"Failed to write debug file: {e}")

    # ------------------------------------------------------------------------
    # Step 1: Basic validation
    # ------------------------------------------------------------------------

    # E1: No images received
    if not images:
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            structured_chat_draft="",
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
            structured_chat_draft="",
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
                    structured_chat_draft="",
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
    structured_parts = []
    all_successful = True
    error_message = ""

    for i, image in enumerate(images):
        # Call appropriate provider for each image
        debug_log(f"[DEBUG] Processing image {i+1} with provider={provider}")
        if provider == "qwen_ocr":
            debug_log(f"[DEBUG] Entering real_qwen_ocr_extract branch")
            success, extracted_text, error_msg = await real_qwen_ocr_extract(image)
        elif provider == "mock":
            debug_log(f"[DEBUG] Entering mock_qwen_ocr_extract branch")
            success, extracted_text, error_msg = await mock_qwen_ocr_extract(image)
        elif provider == "vision_model_v1":
            debug_log(f"[DEBUG] Entering mock_vision_model_v1_extract branch")
            success, extracted_text, error_msg = await mock_vision_model_v1_extract(image)
        else:
            # Only qwen_ocr, mock, and vision_model_v1 are supported in this implementation
            debug_log(f"[DEBUG] Unsupported provider: {provider}")
            success, extracted_text, error_msg = False, "", f"Unsupported provider: {provider}"

        debug_log(f"[DEBUG] Extraction result: success={success}, error_msg={error_msg}, extracted_text_length={len(extracted_text) if extracted_text else 0}")
        if not success:
            # E4: Any single image fails → overall failure (conservative strategy)
            all_successful = False
            error_message = error_msg
            break

        # Add image separator and extracted text
        raw_text_parts.append(f"[Image {i+1}]\n{extracted_text.strip()}")
        # Add to structured parts (without image prefix)
        structured_parts.append(extracted_text.strip())

    # ------------------------------------------------------------------------
    # Step 3: Handle failures
    # ------------------------------------------------------------------------

    if not all_successful:
        return ImageToTextResponse(
            success=False,
            raw_text="",
            merged_text="",
            structured_chat_draft="",
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

    # structured_chat_draft: concatenated structured chat draft without image prefixes
    structured_chat_draft = "\n\n".join(structured_parts).strip()

    # ------------------------------------------------------------------------
    # Step 5: Return successful response
    # ------------------------------------------------------------------------
    # Debug: write provider and implementation
    try:
        with open('debug_implementation.txt', 'w', encoding='utf-8') as f:
            f.write(f"provider={provider}, implementation={provider}_provider\n")
    except Exception as e:
        debug_log(f"Failed to write debug file: {e}")

    return ImageToTextResponse(
        success=True,
        raw_text=raw_text,
        merged_text=merged_text,
        structured_chat_draft=structured_chat_draft,
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
            "implementation": f"{provider}_provider"
        }
    )